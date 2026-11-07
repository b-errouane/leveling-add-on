"""Routenplaner: eine Abfolge von Gelegenheiten, Buendelung und Schlenker ergeben sich aus der Suche.

Grundbausteine (siehe 10-routing-konzepte.md):
- Zustand: Position, Level/XP, offene Quests (Questlog-Platz ist begrenzt), Ruhestein (Heimat,
  Abklingzeit), bekannte Flugpunkte, erlernte Faehigkeitsstufen (Lehrer).
- Wegenetz: zu Fuss, Ruhestein, Flugpunkte. Fuer jedes Ziel gilt der schnellste Weg im aktuellen Zustand,
  deshalb kann derselbe Spieler (gleiches Level, gleiche Quests) je nach Flugpunkten/Ruhestein eine andere
  beste Route haben. Kills auf dem Weg gibt es nur beim Gehen.
- Gelegenheiten: Quest annehmen / abgeben, Mobs toeten (zaehlt fuer alle offenen Quests), Objekt-/Erkundungsziel,
  Grinden (Mobs ohne offenen Questbedarf), Heimat setzen, Flugpunkt entdecken, Lehrer (Errand aus params.json).
  Mengen und Reihenfolge ergeben sich aus der Suche, es gibt keine Gruppen, keinen Radius, keine festen Regeln.
- Zufall: Der gefundene Plan wird mit gewuerfelten Drops nachgespielt (Monte Carlo).

Suche: Strahlsuche nach Zeit-Eimern. Kandidaten-Mengen (Kill-Portionen, Grind-Kandidaten) sind
Suchhilfen aus dem Zustand abgeleitet, keine Spielregeln. Alle Zeiten/Groessen: params.json (Annahmen).
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
    __slots__ = ("t", "pos", "level", "xp", "total", "done", "open", "parent", "act", "rec", "shared",
                 "home", "hearth_ready", "flights", "trained")

    def __init__(self, **kw):
        for k in self.__slots__:
            setattr(self, k, kw.get(k))

    def clone(self, **kw):
        d = {k: getattr(self, k) for k in self.__slots__}
        d.update(kw)
        return State(**d)


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
        self.excluded = set()  # Quests, die der Plan angenommen, aber nie abgegeben hat (Bereinigung)
        # Ressourcen und Wegenetz
        self.slots = int(P["quest_log_slots"])
        self.inns = {}
        for n in npcs.values():
            if n["name"].startswith("Innkeeper") and pts(n, ZONE):
                self.inns[n["id"]] = centroid(pts(n, ZONE))
        self.home0 = self.inns.get(P["initial_home_npc"])
        self.use_hearth = self.home0 is not None
        self.fl_nodes, self.fl_edges = {}, {}  # {id: pos}, {(a, b): Sekunden}; in dieser Zone leer (siehe Doku)
        self.grind_mobs = [m for m in self.spawns if (npcs[str(m)]["rank"] or 0) == 0 and self.spawns[m]]
        self.errands = []
        for e in P.get("errands", []):
            npc = npcs.get(str(e["npc"]))
            if npc and pts(npc, ZONE):
                self.errands.append({**e, "pos": centroid(pts(npc, ZONE))})

    # ---- Grundfunktionen -------------------------------------------------
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

    def speed_mult(self, trained):
        """Kampf-Zeitfaktor durch erlernte Faehigkeitsstufen (Errand 'Lehrer')."""
        f = 1.0
        for e in self.errands:
            f *= (1.0 - e.get("speedup", 0.0)) ** trained
        return f

    def kill_work(self, m, k, mult=1.0):
        """Kampf, Laufen zwischen den Spawns und Warten auf Respawns fuer k Kills (ohne Anreise)."""
        elite = (self.npcs[str(m)]["rank"] or 0) > 0
        ks = kill_seconds(elite) * mult
        n_sp = max(1, len(self.spawns[m]))
        hop = self.nn[m] / P["run_speed_yards_per_s"]
        fight = k * ks
        walk = max(0.0, k - 1) * hop
        rounds = k / n_sp
        wait = 0.0
        if rounds > 1:
            cycle = n_sp * (ks + hop)
            wait = (rounds - 1) * max(0.0, P["mob_respawn_seconds"] - cycle)
        return walk + fight + wait

    def go(self, s, dest):
        """Schnellster Weg von s.pos nach dest im aktuellen Zustand: (Sekunden, Modus, Aenderungen am Zustand)."""
        best = (self.leg(s.pos, dest), "walk", {})
        if s.home is not None and s.t >= s.hearth_ready:
            t = P["hearth_cast_seconds"] + self.leg(s.home, dest)
            if t < best[0]:
                best = (t, "hearth", {"hearth_ready": s.t + P["hearth_cast_seconds"] + P["hearth_cooldown_seconds"]})
        known = [n for n in s.flights if n in self.fl_nodes]
        if len(known) >= 2:
            for a in known:
                to_a = self.leg(s.pos, self.fl_nodes[a])
                for b in known:
                    e = self.fl_edges.get((a, b))
                    if e is None:
                        continue
                    t = to_a + e + self.leg(self.fl_nodes[b], dest)
                    if t < best[0]:
                        best = (t, "flight", {})
        return best

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

    def initial_state(self):
        return State(t=0.0, pos=self.start, level=1, xp=0.0, total=0.0, done=frozenset(), open={}, parent=None,
                     act="start", rec=("start", None, 0.0, (), (), self.start, "walk"), shared=0,
                     home=self.home0, hearth_ready=0.0, flights=frozenset(), trained=0)


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
    ready = 0 if s.home is None or s.t >= s.hearth_ready else 1 + int((s.hearth_ready - s.t) // 600)
    return (round(s.pos[0] / 4), round(s.pos[1] / 4), s.level, s.done, sig, s.home, ready, s.flights, s.trained)


def enroute(w, s, dest, open_, skip_mob=None):
    """Kills auf dem Weg s.pos -> dest: Spawns benoetigter, nicht-elitaerer Mobs im Korridor werden mitgenommen."""
    rem_by_mob = defaultdict(float)
    for kills, _ in open_.values():
        for m, r in kills:
            rem_by_mob[m] = max(rem_by_mob[m], r)
    events, extra_t, extra_xp = [], 0.0, 0.0
    mult = w.speed_mult(s.trained)
    for m, r in rem_by_mob.items():
        if r <= EPS or m == skip_mob or (w.npcs[str(m)]["rank"] or 0) > 0:
            continue
        h = min(w.hits(s.pos, dest, m), r)
        if h > 0:
            xp1, _ = w.mob_xp(s.level, m)
            events.append((m, float(h)))
            extra_t += h * kill_seconds(False) * mult
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
    mult = w.speed_mult(s.trained)

    def emit(dt, mode, upd, level, xp, total, done, open_, act, rec_type, qid, kills_main, events, shared_add, pos):
        ns = s.clone(t=s.t + dt, pos=pos, level=level, xp=xp, total=total, done=done, open=open_, parent=s, act=act,
                     rec=(rec_type, qid, dt, tuple(events), tuple(kills_main), pos, mode), shared=s.shared + shared_add)
        for k, v in upd.items():
            setattr(ns, k, v)
        out.append(ns)

    def travel(dest, skip=None):
        """Weg zu dest inkl. Kills auf dem Weg (nur beim Gehen). Gibt alles zurueck, was die Handlung braucht."""
        dt_go, mode, upd = w.go(s, dest)
        if mode == "walk":
            ev, et, exp_ = enroute(w, s, dest, s.open, skip)
        else:
            ev, et, exp_ = [], 0.0, 0.0
        op = apply_kills(s.open, ev)
        level, xp = w.levelup(s.level, s.xp + exp_)
        helped = max(0, sum(1 for m, _ in ev for kills, _ in s.open.values() if dict(kills).get(m, 0) > EPS) - len(ev))
        return dt_go + et, mode, upd, ev, exp_, op, level, xp, helped

    # 1) Quest annehmen (Questlog-Platz ist begrenzt)
    if not (single and s.open) and len(s.open) < w.slots:
        for q in w.pool:
            qid = q["id"]
            if qid in s.open or qid in w.excluded or not available(q, s.done, s.level, w.race_bit):
                continue
            nd = w.need[qid]
            dt, mode, upd, ev, exp_, op, level, xp, helped = travel(nd["giver"])
            op = dict(op)
            op[qid] = open_entry(w, qid)
            emit(dt + ACCEPT_S, mode, upd, level, xp, s.total + exp_, s.done, op, f"annehmen {q['name']}", "accept", qid, (), ev, helped, nd["giver"])

    # 2) Mobs toeten (zaehlt fuer alle offenen Quests, die den Mob brauchen) und 3) Grinden
    rem_by_mob = {}
    for qid, (kills, _) in s.open.items():
        for m, r in kills:
            if r > EPS:
                rem_by_mob.setdefault(m, []).append(r)
    kill_cands = {}
    for m, rs in rem_by_mob.items():
        n_sp = max(1, len(w.spawns[m]))
        xp1, _ = w.mob_xp(s.level, m)
        to_lvl = math.ceil(max(0.0, w.need_xp.get(s.level, 0) - s.xp) / xp1) if xp1 > 0 else 0
        chunks = {min(rs), max(rs), min(max(rs), float(n_sp))}
        if 0 < to_lvl <= max(rs):
            chunks.add(float(to_lvl))  # bis zum naechsten Level-Up
        kill_cands[m] = (sorted(c for c in chunks if c > EPS), True)
    # Grind-Kandidaten: Mobs ohne offenen Questbedarf, nach XP pro Sekunde (Suchhilfe, kein Gebot)
    ranked = []
    for m in w.grind_mobs:
        if m in kill_cands:
            continue
        xp1, elite = w.mob_xp(s.level, m)
        if xp1 <= 0:
            continue
        entry = w.nearest_spawn(s.pos, m)
        rate = xp1 / (w.leg(s.pos, entry) + kill_seconds(False) * mult)
        ranked.append((rate, m))
    ranked.sort(reverse=True)
    for _, m in ranked[: int(P["grind_candidates"])]:
        n_sp = max(1, len(w.spawns[m]))
        xp1, _ = w.mob_xp(s.level, m)
        to_lvl = math.ceil(max(0.0, w.need_xp.get(s.level, 0) - s.xp) / xp1) if xp1 > 0 else 0
        chunks = {float(n_sp)}
        if 0 < to_lvl <= P["grind_max_chunk"]:
            chunks.add(float(to_lvl))
        kill_cands[m] = (sorted(chunks), False)
    for m, (chunk_list, for_quest) in kill_cands.items():
        entry = w.nearest_spawn(s.pos, m)
        for k in chunk_list:
            dt_go, mode, upd = w.go(s, entry)
            dt = dt_go + w.kill_work(m, k, mult)
            xp1, _ = w.mob_xp(s.level, m)
            op = apply_kills(s.open, [(m, k)])
            level, xp = w.levelup(s.level, s.xp + k * xp1)
            helped = sum(1 for r in rem_by_mob.get(m, []) if r > EPS)
            name = w.npcs[str(m)]["name"]
            if for_quest:
                emit(dt, mode, upd, level, xp, s.total + k * xp1, s.done, op,
                     f"toeten {name} x{k:.0f} (hilft {helped} Quests)", "kill", None, [(m, k)], [], max(0, helped - 1), w.mob_pos[m])
            else:
                emit(dt, mode, upd, level, xp, s.total + k * xp1, s.done, op,
                     f"grinden {name} x{k:.0f}", "grind", None, [(m, k)], [], 0, w.mob_pos[m])

    # 4) Objekt-/Erkundungsziele
    for qid, (kills, misc) in s.open.items():
        if misc > EPS:
            area = centroid(w.need[qid]["misc_area"]) or w.need[qid]["giver"]
            dt, mode, upd, ev, exp_, op, level, xp, helped = travel(area)
            op = dict(op)
            op[qid] = (op[qid][0], 0.0)
            emit(dt + misc, mode, upd, level, xp, s.total + exp_, s.done, op, f"erledigen {w.q[qid]['name']}", "misc", qid, (), ev, helped, area)

    # 5) Abgeben
    for qid, (kills, misc) in s.open.items():
        if misc <= EPS and all(r <= EPS for _, r in kills):
            nd = w.need[qid]
            dest = nd["ender"] or nd["giver"]
            dt, mode, upd, ev, exp_, op, level, xp, helped = travel(dest)
            op = {k: v for k, v in op.items() if k != qid}
            gain = qxp_at(w.q[qid], level, w.table, w.est_tier)
            level, xp = w.levelup(level, xp + gain)
            emit(dt + TURNIN_S, mode, upd, level, xp, s.total + exp_ + gain, s.done | {qid}, op,
                 f"abgeben {w.q[qid]['name']}", "turnin", qid, (), ev, helped, dest)

    # 6) Heimat setzen (Ruhestein): Gelegenheit, die spaetere Wege verkuerzt
    for inn_id, ipos in w.inns.items():
        if s.home != ipos:
            dt, mode, upd = w.go(s, ipos)
            emit(dt + P["sethome_seconds"], mode, {**upd, "home": ipos}, s.level, s.xp, s.total, s.done, s.open,
                 f"Heimat setzen: {w.npcs[str(inn_id)]['name']}", "sethome", None, (), [], 0, ipos)

    # 7) Flugpunkt entdecken
    for node, npos in w.fl_nodes.items():
        if node not in s.flights:
            dt, mode, upd = w.go(s, npos)
            emit(dt + P["flight_discover_seconds"], mode, {**upd, "flights": s.flights | {node}}, s.level, s.xp, s.total,
                 s.done, s.open, f"Flugpunkt entdecken: {node}", "discover", None, (), [], 0, npos)

    # 8) Errands (z. B. Lehrer): neue Faehigkeitsstufen lernen verkuerzt kuenftige Kaempfe
    for e in w.errands:
        avail = sum(1 for lvl in e["steps"] if lvl <= s.level) - s.trained
        if avail > 0:
            dt, mode, upd = w.go(s, e["pos"])
            emit(dt + e["seconds"], mode, {**upd, "trained": s.trained + avail}, s.level, s.xp, s.total, s.done, s.open,
                 f"{e['id']} besuchen ({avail} neue Stufe(n))", "errand", None, (), [], 0, e["pos"])
    return out


def plan(w, target, beam, bucket, single, horizon=4 * 3600):
    start = w.initial_state()
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


def plan_refined(w, target, beam, bucket, single, max_rounds=4):
    """Plan suchen und bereinigen: Quests, die am Ende offen sind (angenommen, nie abgegeben), kosten nur
    Zeit. Sie werden aus dem Pool genommen und der Plan wird neu gesucht, solange das nicht langsamer ist."""
    w.excluded = set()
    best = plan(w, target, beam, bucket, single)
    for _ in range(max_rounds):
        if best is None or not best.open:
            break
        w.excluded = w.excluded | set(best.open)
        cand = plan(w, target, beam, bucket, single)
        if cand is not None and cand.t <= best.t + 1.0:
            best = cand
        else:
            w.excluded = w.excluded - set(best.open)
            break
    return best


def trace(s):
    steps = []
    while s is not None:
        steps.append(s)
        s = s.parent
    return list(reversed(steps))


def _geom(rng, p):
    u = rng.random()
    return 1 if p >= 1 else max(1, math.ceil(math.log(1 - u) / math.log(1 - p)))


def replay(w, recs, target, rng):
    """Spielt den Plan mit gewuerfelten Drops nach. Fehlende Items kosten Zusatz-Kills (Weg hin und zurueck)."""
    t, level, xp = 0.0, 1, 0.0
    open_ = {}
    for rec in recs[1:]:
        typ, qid, dt, events, kills_main, end = rec[:6]
        t += dt
        for m, k in list(events) + list(kills_main):
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
            for m, need_k in st["req"].items():
                miss = need_k - st["recv"][m]
                if miss > 0.5:
                    elite = (w.npcs[str(m)]["rank"] or 0) > 0
                    t += 2 * w.leg(end, w.mob_pos[m]) + miss * kill_seconds(elite)
                    xp += miss * w.mob_xp(level, m)[0]
            xp += qxp_at(w.q[qid], level, w.table, w.est_tier)
        level, xp = w.levelup(level, xp)
        if level >= target:
            return t
    return t


def monte_carlo(w, end, target, runs, seed=1):
    recs = [s.rec for s in trace(end)]
    rng = random.Random(seed)
    ts = sorted(replay(w, recs, target, rng) for _ in range(runs))
    return {"mean": statistics.mean(ts), "median": ts[len(ts) // 2], "p10": ts[int(0.1 * len(ts))], "p90": ts[int(0.9 * len(ts))]}


def build_world(race_bit=1):
    return World(load("quests.json"), load("npcs.json"), load("objects.json"), load("items.json"),
                 load("drops.json"), load("quest_xp_table.json"), race_bit)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target-level", type=int, default=10)
    ap.add_argument("--beam", type=int, default=150)
    ap.add_argument("--bucket", type=float, default=20.0)
    ap.add_argument("--race-bit", type=int, default=1)
    ap.add_argument("--with-trainer", action="store_true", help="Beispiel-Errand 'Lehrer' aus params.json aktivieren")
    ap.add_argument("--set", action="append", default=[], metavar="NAME=WERT",
                    help="Parameter aus params.json ueberschreiben (Zahlen), z. B. --set seconds_per_kill=25")
    a = ap.parse_args()
    for kv in a.set:
        name, val = kv.split("=", 1)
        P[name] = float(val)
    if a.with_trainer:
        P["errands"] = [P["_errands_beispiel"]]
    w = build_world(a.race_bit)
    lines = [f"# Routenplanung (Strahlsuche + Monte Carlo), Mensch, Level 1 -> {a.target_level}", "",
             "ANNAHMEN (nicht gemessen): `pipeline/config/params.json`. Buendelung, Schlenker, Ruhestein und Grinden ergeben sich aus der Suche, es gibt keine Gruppen oder Schwellen.",
             f"Suchparameter: Strahlbreite {a.beam}, Zeit-Eimer {a.bucket:.0f} s. Zufall: {P['mc_runs']} Nachspielungen mit gewuerfelten Drops.",
             f"Questlog-Plaetze: {w.slots}. Ruhestein-Heimat am Start: {'ja' if w.use_hearth else 'nein'}. Errands: {[e['id'] for e in w.errands] or 'keine'}.", ""]
    results = {}
    for label, single in (("frei (beliebig viele Quests offen)", False), ("Vergleich: immer nur eine Quest offen", True)):
        end = plan_refined(w, a.target_level, a.beam, a.bucket, single)
        results[label] = end
        if end is None:
            lines += [f"## {label}", "Kein Weg gefunden.", ""]
            continue
        steps = trace(end)
        mc = monte_carlo(w, end, a.target_level, P["mc_runs"])
        max_open = max(len(s.open) for s in steps)
        modes = defaultdict(int)
        kinds = defaultdict(int)
        for s in steps[1:]:
            modes[s.rec[6]] += 1
            kinds[s.rec[0]] += 1
        acts = [f"| {s.t/60:.1f} | {s.level} | {len(s.open)} | {s.act}{' [' + s.rec[6] + ']' if s.rec[6] != 'walk' else ''} |" for s in steps[1:]]
        lines += [f"## {label}",
                  f"Plan (Erwartungswerte): Level {a.target_level} nach **{end.t/60:.1f} min**, {len(end.done)} Quests abgegeben, "
                  f"bis zu {max_open} gleichzeitig offen, geteilte Kills: {end.shared}",
                  f"Handlungen: {dict(kinds)}. Wegarten: {dict(modes)}",
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
