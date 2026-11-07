"""Routenplaner (Prototyp): Buendelung ergibt sich aus der Planung, nicht aus vorgegebenen Gruppen.

Der Planer sucht eine Abfolge von Handlungen: Quest annehmen, Mobs toeten, Objekt-/Erkundungsziel
erledigen, Quest abgeben. Offene Quests teilen sich Kills automatisch. Ob mehrere Quests gleichzeitig
offen sind, entscheidet allein die Zeit: Es gibt keine Gruppen, keinen Radius, keine Schwellenwerte.

Modell des Spielers:
- Position als Zustand, Wege als Linienzug durch die Stationen (Luftlinie in Yards).
- Mobs als echte Spawn-Punkte: Anlaufen des naechsten Spawns, Laufweg zwischen den Kills (mittlerer
  Nachbarabstand), Wartezeit auf Respawns, wenn mehr Kills gebraucht werden als Spawns da sind.
- Kills auf dem Weg: Spawns benoetigter Mobs entlang einer Strecke werden mitgenommen.
- Zufall: Der gefundene Plan wird mehrfach mit gewuerfelten Drops nachgespielt (Monte Carlo).

Suche: Strahlsuche nach Zeit-Eimern (Suchparameter, keine Spielregel).
Annahmen fuer Zeiten und Groessen: pipeline/config/params.json (nicht gemessen).
Aufruf: python -m pipeline.derive.planner [--target-level 10] [--beam 150] [--bucket 20]
"""
import argparse
import math
import random
import statistics
from collections import defaultdict
from pathlib import Path

from pipeline.derive.derive import P, centroid, kill_seconds, load, mob_base_xp, pts, typical_tier, yards
from pipeline.derive.route import ZONE, ZONES, available, needs, qxp_at

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "data/reports"
ACCEPT_S, TURNIN_S = 10.0, 15.0  # Aufteilung des Quest-Overheads (zusammen 25 s)
EPS = 0.05


class State:
    __slots__ = ("t", "pos", "level", "xp", "total", "done", "open", "parent", "act", "rec", "shared")

    def __init__(self, t, pos, level, xp, total, done, open_, parent, act, rec, shared):
        self.t, self.pos, self.level, self.xp, self.total = t, pos, level, xp, total
        self.done, self.open, self.parent, self.act, self.rec, self.shared = done, open_, parent, act, rec, shared


def _seg_dist(p, a, b, sx, sy):
    """Abstand Punkt p zur Strecke a-b in Yards (Karten-Prozent -> Yards getrennt je Achse)."""
    px, py, ax, ay, bx, by = p[0] * sx, p[1] * sy, a[0] * sx, a[1] * sy, b[0] * sx, b[1] * sy
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    u = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
    return math.hypot(px - (ax + u * dx), py - (ay + u * dy))


class World:
    def __init__(self, quests, npcs, objects, items, drops, table, race_bit):
        self.npcs, self.table, self.race_bit = npcs, table, race_bit
        self.est_tier = typical_tier(quests, table)
        pool = [q for q in quests.values() if q["zone_or_sort"] in ZONES and not q["placeholder"]]
        self.need = {q["id"]: needs(q, npcs, objects, items, drops) for q in pool}
        self.pool = [q for q in pool if self.need[q["id"]]["giver"] is not None
                     and (q["started_by"]["npc"] or q["started_by"]["object"])]
        self.q = {q["id"]: q for q in self.pool}
        self.scale = tuple(P["zone_size_yards"].get(str(ZONE), P["zone_size_yards"]["default"]))
        self.spawns, self.mob_pos, self.nn = {}, {}, {}
        for n in self.need.values():
            for m in n["kills"]:
                if m in self.spawns:
                    continue
                sp = pts(npcs[str(m)], ZONE)
                self.spawns[m] = sp
                self.mob_pos[m] = centroid(sp)
                if len(sp) > 1:
                    d = [min(yards(a, b, ZONE) for b in sp if b is not a) for a in sp]
                    self.nn[m] = sum(d) / len(d)
                else:
                    self.nn[m] = 0.0
        self.need_xp = {int(k): v for k, v in P["xp_to_next_level"].items() if k.isdigit()}
        self.start = centroid(pts(npcs["197"], ZONE))  # Marshal McBride
        self._hits = {}

    def mob_xp(self, level, m):
        npc = self.npcs[str(m)]
        ml = round(((npc["min_level"] or level) + (npc["max_level"] or level)) / 2)
        elite = (npc["rank"] or 0) > 0
        return mob_base_xp(level, ml) * (P["elite_xp_multiplier"] if elite else 1.0), elite

    def leg(self, a, b):
        return (yards(a, b, ZONE) or 0.0) / P["run_speed_yards_per_s"]

    def levelup(self, level, xp):
        while level in self.need_xp and xp >= self.need_xp[level]:
            xp -= self.need_xp[level]
            level += 1
        return level, xp

    def nearest_spawn(self, pos, m):
        return min(self.spawns[m], key=lambda p: yards(pos, p, ZONE))

    def kill_time(self, pos, m, k):
        """Zeit fuer k Kills an Mob m: Anlaufen, Kampf, Laufen zwischen Spawns, Warten auf Respawns."""
        npc_elite = (self.npcs[str(m)]["rank"] or 0) > 0
        ks = kill_seconds(npc_elite)
        entry = self.nearest_spawn(pos, m)
        n_sp = max(1, len(self.spawns[m]))
        hop = self.nn[m] / P["run_speed_yards_per_s"]
        walk = self.leg(pos, entry) + max(0.0, k - 1) * hop
        fight = k * ks
        rounds = k / n_sp
        wait = 0.0
        if rounds > 1:
            cycle = n_sp * (ks + hop)
            wait = (rounds - 1) * max(0.0, P["mob_respawn_seconds"] - cycle)
        return walk + fight + wait

    def hits(self, a, b, m):
        """Wie viele Spawns von m liegen im Korridor entlang der Strecke a->b (memoisiert)."""
        key = (a, b, m)
        if key not in self._hits:
            if a == b:
                self._hits[key] = 0
            else:
                c = P["corridor_yards"]
                self._hits[key] = sum(1 for p in self.spawns[m] if _seg_dist(p, a, b, self.scale[0] / 100, self.scale[1] / 100) <= c)
        return self._hits[key]


def open_entry(w, qid):
    nd = w.need[qid]
    misc = nd["obj_sec"] if nd["misc_area"] or (nd["obj_sec"] and not nd["kills"]) else 0.0
    return (tuple(sorted(nd["kills"].items())), misc)


def credit(w, s):
    """Bewerteter Fortschritt: bisherige XP plus anteilig die XP offener Quests, abzueglich der
    Zeit fuers Abgeben, umgerechnet in XP mit der bisherigen Rate des Plans (Opportunitaetskosten)."""
    c = s.total
    rate = max(s.total, 1.0) / max(s.t, 60.0)
    for qid, (kills, misc) in s.open.items():
        nd = w.need[qid]
        tot = sum(nd["kills"].values()) + (nd["obj_sec"] / P["seconds_per_kill"] if nd["obj_sec"] else 0.0)
        if tot > 0:
            rem = sum(r for _, r in kills) + misc / P["seconds_per_kill"]
            frac = max(0.0, 1 - rem / tot)
            dest = nd["ender"] or nd["giver"]
            turn_cost = (w.leg(s.pos, dest) + TURNIN_S) * rate
            c += frac * max(0.0, qxp_at(w.q[qid], s.level, w.table, w.est_tier) - turn_cost)
    return c


def key(w, s):
    sig = tuple(sorted((qid, tuple(round(r) for _, r in k), misc > 0) for qid, (k, misc) in s.open.items()))
    return (round(s.pos[0] / 4), round(s.pos[1] / 4), s.level, s.done, sig)


def enroute(w, s, dest, open_, skip_mob=None):
    """Kills auf dem Weg s.pos -> dest: Spawns benoetigter, nicht-elitaerer Mobs im Korridor werden mitgenommen."""
    rem_by_mob = defaultdict(float)
    for kills, _ in open_.values():
        for m, r in kills:
            rem_by_mob[m] = max(rem_by_mob[m], r)
    events, extra_t, extra_xp, level, xp = [], 0.0, 0.0, s.level, s.xp
    for m, r in rem_by_mob.items():
        if r <= EPS or m == skip_mob or (w.npcs[str(m)]["rank"] or 0) > 0:
            continue
        h = min(w.hits(s.pos, dest, m), r)
        if h > 0:
            xp1, _ = w.mob_xp(level, m)
            events.append((m, float(h)))
            extra_t += h * kill_seconds(False)
            extra_xp += h * xp1
    return events, extra_t, extra_xp


def apply_kills(open_, events):
    op = {}
    for qid, (kills, misc) in open_.items():
        km = dict(kills)
        for m, h in events:
            if m in km:
                km[m] = max(0.0, km[m] - h)
        op[qid] = (tuple(sorted(km.items())), misc)
    return op


def expand(w, s, single):
    out = []

    def finish(dt, pos, level, xp, total, done, open_, act, rec_type, qid, kills_main, events, shared_add):
        # Kills auf dem Weg wirken auf die bereits offenen Quests (vor dem eigenen Effekt der Handlung)
        out.append(State(s.t + dt, pos, level, xp, total, done, open_, s, act,
                         (rec_type, qid, dt, tuple(events), tuple(kills_main), pos), s.shared + shared_add))

    def en_route_then(dest, skip=None):
        ev, et, exp_ = enroute(w, s, dest, s.open, skip)
        op = apply_kills(s.open, ev)
        level, xp = w.levelup(s.level, s.xp + exp_)
        helped = sum(1 for m, _ in ev for kills, _ in s.open.values() if dict(kills).get(m, 0) > EPS) - len(ev)
        return ev, et, exp_, op, level, xp, max(0, helped)

    # 1) Quest annehmen
    if not (single and s.open):
        for q in w.pool:
            qid = q["id"]
            if qid in s.open or not available(q, s.done, s.level, w.race_bit):
                continue
            nd = w.need[qid]
            ev, et, exp_, op, level, xp, helped = en_route_then(nd["giver"])
            op = dict(op)
            op[qid] = open_entry(w, qid)
            dt = w.leg(s.pos, nd["giver"]) + ACCEPT_S + et
            finish(dt, nd["giver"], level, xp, s.total + exp_, s.done, op, f"annehmen {q['name']}", "accept", qid, (), ev, helped)
    # 2) Mobs toeten
    rem_by_mob = {}
    for qid, (kills, _) in s.open.items():
        for m, r in kills:
            if r > EPS:
                rem_by_mob.setdefault(m, []).append(r)
    for m, rs in rem_by_mob.items():
        for k in sorted({min(rs), max(rs)}):
            dt = w.kill_time(s.pos, m, k)
            xp1, _ = w.mob_xp(s.level, m)
            op = apply_kills(s.open, [(m, k)])
            level, xp = w.levelup(s.level, s.xp + k * xp1)
            helped = sum(1 for r in rs if r > EPS)
            end = w.mob_pos[m]
            finish(dt, end, level, xp, s.total + k * xp1, s.done, op,
                   f"toeten {w.npcs[str(m)]['name']} x{k:.0f} (hilft {helped} Quests)", "kill", None, [(m, k)], [], helped - 1)
    # 3) Objekt-/Erkundungsziele
    for qid, (kills, misc) in s.open.items():
        if misc > EPS:
            area = centroid(w.need[qid]["misc_area"]) or w.need[qid]["giver"]
            ev, et, exp_, op, level, xp, helped = en_route_then(area)
            op = dict(op)
            op[qid] = (op[qid][0], 0.0)
            dt = w.leg(s.pos, area) + misc + et
            finish(dt, area, level, xp, s.total + exp_, s.done, op, f"erledigen {w.q[qid]['name']}", "misc", qid, (), ev, helped)
    # 4) Abgeben
    for qid, (kills, misc) in s.open.items():
        if misc <= EPS and all(r <= EPS for _, r in kills):
            nd = w.need[qid]
            dest = nd["ender"] or nd["giver"]
            ev, et, exp_, op, level, xp, helped = en_route_then(dest)
            op = {k: v for k, v in op.items() if k != qid}
            gain = qxp_at(w.q[qid], level, w.table, w.est_tier)
            level, xp = w.levelup(level, xp + gain)
            dt = w.leg(s.pos, dest) + TURNIN_S + et
            finish(dt, dest, level, xp, s.total + exp_ + gain, s.done | {qid}, op, f"abgeben {w.q[qid]['name']}",
                   "turnin", qid, (), ev, helped)
    return out


def plan(w, target, beam, bucket, single, horizon=4 * 3600):
    start = State(0.0, w.start, 1, 0.0, 0.0, frozenset(), {}, None, "start", ("start", None, 0.0, (), (), w.start), 0)
    buckets = {0: [start]}
    best = None
    for b in range(int(horizon // bucket) + 1):
        states = buckets.pop(b, [])
        if not states:
            continue
        if best is not None and b * bucket > best.t:
            break
        uniq = {}
        for s in states:
            k = key(w, s)
            if k not in uniq or credit(w, s) > credit(w, uniq[k]):
                uniq[k] = s
        ranked = sorted(uniq.values(), key=lambda s: -credit(w, s))[:beam]
        for s in ranked:
            for n in expand(w, s, single):
                if n.level >= target:
                    if best is None or n.t < best.t:
                        best = n
                    continue
                buckets.setdefault(int(n.t // bucket), []).append(n)
    return best


def trace(s):
    steps = []
    while s is not None:
        steps.append(s)
        s = s.parent
    return list(reversed(steps))


def _geom(rng, p):
    """Anzahl Versuche bis zum ersten Erfolg (Erfolgswahrscheinlichkeit p)."""
    u = rng.random()
    return 1 if p >= 1 else max(1, math.ceil(math.log(1 - u) / math.log(1 - p)))


def replay(w, recs, target, rng):
    """Spielt den Plan mit gewuerfelten Drops nach. Fehlende Items kosten Zusatz-Kills (Weg hin und zurueck)."""
    t, pos, level, xp = 0.0, w.start, 1, 0.0
    open_ = {}
    for rec in recs[1:]:
        typ, qid, dt, events, kills_main, end = rec
        t += dt
        got = list(events) + list(kills_main)
        for m, k in got:
            xp1, _ = w.mob_xp(level, m)
            xp += k * xp1
            for st in open_.values():
                st["recv"][m] += k
        if typ == "accept":
            nd = w.need[qid]
            req = dict(nd["direct_kills"])
            for m, n, rate in nd["item_needs"]:
                req[m] = max(req.get(m, 0), sum(_geom(rng, rate) for _ in range(int(round(n)))))
            open_[qid] = {"recv": defaultdict(float), "req": req}
        elif typ == "turnin":
            st = open_.pop(qid)
            # Einsammeln fehlender Items: Zusatz-Kills, Weg zum Spawn und zurueck
            for m, need_k in st["req"].items():
                miss = need_k - st["recv"][m]
                if miss > 0.5:
                    npc_elite = (w.npcs[str(m)]["rank"] or 0) > 0
                    t += 2 * w.leg(end, w.mob_pos[m]) + miss * kill_seconds(npc_elite)
                    xp += miss * w.mob_xp(level, m)[0]
            xp += qxp_at(w.q[qid], level, w.table, w.est_tier)
        pos = end
        level, xp = w.levelup(level, xp)
        if level >= target:
            return t
    return t


def monte_carlo(w, end, target, runs, seed=1):
    recs = [s.rec for s in trace(end)]
    rng = random.Random(seed)
    ts = sorted(replay(w, recs, target, rng) for _ in range(runs))
    return {"mean": statistics.mean(ts), "median": ts[len(ts) // 2], "p10": ts[int(0.1 * len(ts))], "p90": ts[int(0.9 * len(ts))]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target-level", type=int, default=10)
    ap.add_argument("--beam", type=int, default=150)
    ap.add_argument("--bucket", type=float, default=20.0)
    ap.add_argument("--race-bit", type=int, default=1)
    a = ap.parse_args()
    w = World(load("quests.json"), load("npcs.json"), load("objects.json"), load("items.json"),
              load("drops.json"), load("quest_xp_table.json"), a.race_bit)
    lines = [f"# Routenplanung (Strahlsuche + Monte Carlo), Mensch, Level 1 -> {a.target_level}", "",
             "ANNAHMEN (nicht gemessen): `pipeline/config/params.json`. Buendelung ergibt sich aus der Suche, es gibt keine Gruppen oder Schwellen.",
             f"Suchparameter: Strahlbreite {a.beam}, Zeit-Eimer {a.bucket:.0f} s. Zufall: {P['mc_runs']} Nachspielungen mit gewuerfelten Drops.", ""]
    results = {}
    for label, single in (("frei (beliebig viele Quests offen)", False), ("Vergleich: immer nur eine Quest offen", True)):
        end = plan(w, a.target_level, a.beam, a.bucket, single)
        results[label] = end
        if end is None:
            lines += [f"## {label}", "Kein Weg gefunden.", ""]
            continue
        steps = trace(end)
        mc = monte_carlo(w, end, a.target_level, P["mc_runs"])
        max_open = max(len(s.open) for s in steps)
        acts = [f"| {s.t/60:.1f} | {s.level} | {len(s.open)} | {s.act} |" for s in steps[1:]]
        lines += [f"## {label}",
                  f"Plan (Erwartungswerte): Level {a.target_level} nach **{end.t/60:.1f} min**, {len(end.done)} Quests abgegeben, "
                  f"bis zu {max_open} gleichzeitig offen, geteilte Kills: {end.shared}",
                  f"Mit gewuerfelten Drops (gleicher Plan): Mittel {mc['mean']/60:.1f} min, Median {mc['median']/60:.1f} min, "
                  f"10 %-Quantil {mc['p10']/60:.1f} min, 90 %-Quantil {mc['p90']/60:.1f} min", "",
                  "| Min | Level | offen | Handlung |", "|---|---|---|---|", *acts, ""]
    f, o = results.get("frei (beliebig viele Quests offen)"), results.get("Vergleich: immer nur eine Quest offen")
    if f and o:
        lines.append(f"Vergleich (Erwartungswerte): frei {f.t/60:.1f} min, eine Quest zur Zeit {o.t/60:.1f} min "
                     f"({100*(1-f.t/o.t):.0f} % weniger). Ohne Gewaehr, siehe Annahmen.")
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "planner_report.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
