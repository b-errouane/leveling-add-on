"""Stufe 5 (Prototyp): Buendel und Route (Greedy-Simulation) fuer die Startgebiete.

Idee: Quests werden nicht einzeln, sondern als Buendel pro Quest-Geber-Ort bewertet. Gleiche Mobs in
mehreren Quests zaehlen nur einmal (Verstaerkungseffekt). Die Simulation waehlt wiederholt das Buendel
mit den meisten XP/h, wendet Level-Ups an und verfolgt freigeschaltete Folgequests.

Alle Zeit- und Groessenwerte sind Annahmen (pipeline/config/params.json), keine Messwerte.
Aufruf: python -m pipeline.derive.route [--target-level 10] [--race-bit 1]
"""
import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

from pipeline.derive.derive import (P, centroid, counts_from_text, kill_seconds, load, mob_base_xp, pts,
                                    typical_tier, yards, UNKNOWN_TRAVEL_YARDS)

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "data/reports"
ZONE = 12  # Koordinatenraum von Northshire (9) und Elwynn (12)
ZONES = {9, 12}


def qxp_at(q, level, table, est_tier):
    if q["xp"]:
        base = q["xp"]["xp"]
    else:
        row = table.get(str(q["quest_level"] or level))
        base = row[est_tier] if row else 0
    diff = max(0, level - (q["quest_level"] or level))
    f = P["quest_xp_factor_by_level_diff"].get(str(min(diff, 9)), 1.0)
    return base * f


def needs(q, npcs, objects, items, drops):
    """Was die Quest braucht: Kills je Mob, Objekt-Sekunden, Zielgebiet, Positionen."""
    kills, obj_sec, area, misc_area = defaultdict(float), 0.0, [], []
    direct_kills, item_needs = {}, []  # fuer die Zufallssimulation: feste Kills und (Mob, Menge, Drop-Rate)
    counts, _ = counts_from_text(q)
    idx = 0
    for o in q["objectives"]["creature"]:
        n = counts[idx] if idx < len(counts) else 1
        idx += 1
        npc = npcs.get(str(o["id"]))
        if npc:
            kills[npc["id"]] = max(kills[npc["id"]], n)
            direct_kills[npc["id"]] = max(direct_kills.get(npc["id"], 0), n)
            area += pts(npc, ZONE)
    for o in q["objectives"]["object"]:
        n = counts[idx] if idx < len(counts) else 1
        idx += 1
        area += pts(objects.get(str(o["id"])), ZONE)
        misc_area += pts(objects.get(str(o["id"])), ZONE)
        obj_sec += n * P["seconds_per_object_interaction"]
    for o in q["objectives"]["item"]:
        n = counts[idx] if idx < len(counts) else 1
        idx += 1
        it = items.get(str(o["id"])) or {}
        rates = drops.get(str(o["id"]), {})
        srcs = [(npcs.get(str(x)), rates.get(str(x))) for x in it.get("npc_drops", [])]
        srcs = [(npc, r) for npc, r in srcs if npc and pts(npc, ZONE)]
        rated = [(npc, r) for npc, r in srcs if r]
        if rated:
            # Bestes Verhaeltnis aus Drop-Rate und Naehe zum Ziel-Gebiet der uebrigen Ziele waere dynamischer,
            # braucht aber die Position zur Planungszeit. Vorlaeufig: die Quelle mit der besten Rate.
            best = max(r for _, r in rated)
            npc = max(rated, key=lambda x: x[1])[0]
            rate = best / 100.0
        elif srcs:
            npc, rate = srcs[0][0], P["unknown_drop_rate"]
        else:
            obj_src = [objects.get(str(x)) for x in it.get("object_drops", [])]
            for ob in obj_src:
                area += pts(ob, ZONE)
                misc_area += pts(ob, ZONE)
            obj_sec += n * P["seconds_per_object_interaction"]
            continue
        kills[npc["id"]] = max(kills[npc["id"]], n / max(rate, 0.01))
        item_needs.append((npc["id"], n, max(rate, 0.01)))
        area += pts(npc, ZONE)
    trig = q.get("trigger_end")
    if trig:
        area += [tuple(p) for p in trig["spawns"].get(str(ZONE), [])]
        misc_area += [tuple(p) for p in trig["spawns"].get(str(ZONE), [])]
    pos = lambda ids, store: next((c for c in (centroid(pts(store.get(str(i)), ZONE)) for i in ids) if c), None)
    giver = pos(q["started_by"]["npc"], npcs) or pos(q["started_by"]["object"], objects)
    ender = pos(q["finished_by"]["npc"], npcs) or pos(q["finished_by"]["object"], objects)
    return {"kills": dict(kills), "obj_sec": obj_sec, "area": area, "misc_area": misc_area,
            "giver": giver, "ender": ender, "direct_kills": direct_kills, "item_needs": item_needs}


def bundle_eval(qs, need, level, cur, npcs, table, est_tier):
    """Zeit und XP eines Buendels. Gleiche Mobs zaehlen nur einmal (Maximum statt Summe)."""
    merged = defaultdict(float)
    obj_sec, area, givers, enders = 0.0, [], [], []
    for q in qs:
        nd = need[q["id"]]
        for mob, k in nd["kills"].items():
            merged[mob] = max(merged[mob], k)
        obj_sec += nd["obj_sec"]
        area += nd["area"]
        givers.append(nd["giver"])
        enders.append(nd["ender"] or nd["giver"])
    mob_xp, kill_sec = 0.0, 0.0
    for mob, k in merged.items():
        npc = npcs[str(mob)]
        elite = (npc["rank"] or 0) > 0
        ml = round(((npc["min_level"] or level) + (npc["max_level"] or level)) / 2)
        mob_xp += k * mob_base_xp(level, ml) * (P["elite_xp_multiplier"] if elite else 1.0)
        kill_sec += k * kill_seconds(elite)
    g, a, e = centroid(givers), centroid(area), centroid(enders)
    legs = [cur, g] + ([a] if a else []) + [e or g]
    dist = sum(yards(legs[i], legs[i + 1], ZONE) or 0.0 for i in range(len(legs) - 1))
    sec = dist / P["run_speed_yards_per_s"] + kill_sec + obj_sec + P["seconds_overhead_per_quest"] * len(qs)
    quest_xp = sum(qxp_at(q, level, table, est_tier) for q in qs)
    return {"seconds": sec, "xp": quest_xp + mob_xp, "end": e or g, "kills": sum(merged.values()),
            "shared_saved_kills": sum(max(need[q["id"]]["kills"].values(), default=0) * 0 for q in qs)}


def _rate(ev):
    return ev["xp"] / ev["seconds"] if ev["seconds"] else 0.0


def best_bundle(cands, need, level, cur, npcs, table, est_tier, allow_bundle):
    """Dynamisches Buendel ohne feste Gruppen oder Schwellen.

    Jede verfuegbare Quest ist ein moeglicher Startpunkt (Seed). Von dort wird lokal gesucht:
    eine Quest hinzufuegen, entfernen oder tauschen, solange die XP/h des Buendels steigen.
    Entfernung, Mob-Ueberlappung und Zeit gehen allein ueber das Zeitmodell ein. Es gibt keinen
    Radius und keine Mindestwerte. Gewinner ist das Buendel mit den meisten XP/h.
    """
    ev = lambda qs: bundle_eval(qs, need, level, cur, npcs, table, est_tier)
    best = None
    for seed in cands:
        qs = [seed]
        rate = _rate(ev(qs))
        while allow_bundle:
            options = []
            for q in cands:  # hinzufuegen
                if q not in qs:
                    options.append(qs + [q])
            if len(qs) > 1:  # entfernen
                for q in qs:
                    options.append([x for x in qs if x is not q])
            scored = [(o, _rate(ev(o))) for o in options]
            if not scored:
                break
            top, r = max(scored, key=lambda t: t[1])
            if r > rate * 1.000001:
                qs, rate = top, r
            else:
                break
        if best is None or rate > best[2]:
            best = (qs, ev(qs), rate)
    return best[0], best[1]


def available(q, done, level, race_bit):
    if q["placeholder"] or q["id"] in done or (q["required_level"] or 1) > level:
        return False
    mask = q["required_races"]
    if mask and not (mask & race_bit):
        return False
    if q["prequest_group"] and not all(p in done for p in q["prequest_group"]):
        return False
    if q["prequest_single"] and not any(p in done for p in q["prequest_single"]):
        return False
    if any(x in done for x in q["exclusive_to"]):
        return False
    return True


def simulate(quests, npcs, objects, items, drops, table, est_tier, target, race_bit, allow_bundle):
    pool = [q for q in quests.values() if q["zone_or_sort"] in ZONES and not q["placeholder"]]
    need = {q["id"]: needs(q, npcs, objects, items, drops) for q in pool}
    pool = [q for q in pool if need[q["id"]]["giver"] is not None and (q["started_by"]["npc"] or q["started_by"]["object"])]
    # Startposition: Marshal McBride (NPC 197)
    cur = centroid(pts(npcs["197"], ZONE))
    level, xp, t, done, steps = 1, 0.0, 0.0, set(), []
    need_xp = {int(k): v for k, v in P["xp_to_next_level"].items() if k.isdigit()}
    while level < target:
        cands = [q for q in pool if available(q, done, level, race_bit)]
        if not cands:
            break
        sel, ev = best_bundle(cands, need, level, cur, npcs, table, est_tier, allow_bundle)
        t += ev["seconds"]
        xp += ev["xp"]
        cur = ev["end"]
        for q in sel:
            done.add(q["id"])
        lvl_before = level
        while level in need_xp and xp >= need_xp[level]:
            xp -= need_xp[level]
            level += 1
        steps.append({"quests": [(q["id"], q["name"]) for q in sel], "level_before": lvl_before, "level_after": level,
                      "xp": round(ev["xp"]), "seconds": round(ev["seconds"]), "total_seconds": round(t)})
    return {"steps": steps, "level": level, "seconds": t, "done": done, "pool": pool}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target-level", type=int, default=10)
    ap.add_argument("--race-bit", type=int, default=1, help="1 = Mensch")
    a = ap.parse_args()
    quests, npcs, objects, items = load("quests.json"), load("npcs.json"), load("objects.json"), load("items.json")
    drops, table = load("drops.json"), load("quest_xp_table.json")
    est_tier = typical_tier(quests, table)
    res = {}
    for label, bundle in (("mit Buendeln", True), ("ohne Buendel (je Quest einzeln)", False)):
        res[label] = simulate(quests, npcs, objects, items, drops, table, est_tier, a.target_level, a.race_bit, bundle)
    lines = [f"# Routen-Simulation (Prototyp), Mensch, Level 1 -> {a.target_level}", "",
             "ANNAHMEN (nicht gemessen): siehe `pipeline/config/params.json`. Nur Quests aus Northshire/Elwynn. Buendel ohne feste Gruppen: lokale Suche aus jeder verfuegbaren Quest heraus.",
             "Neue Quests ohne XP-Angabe sind mit der typischen Stufe geschaetzt (siehe derived_report.md).", ""]
    for label, r in res.items():
        lines += [f"## {label}", f"Erreicht: Level {r['level']} nach {r['seconds']/60:.0f} min ({len(r['done'])} Quests, {len(r['steps'])} Schritte)", "",
                  "| # | Level | Quests | XP | Zeit (s) | Gesamt (min) |", "|---|---|---|---|---|---|"]
        for i, s in enumerate(r["steps"], 1):
            names = "; ".join(n[:26] for _, n in s["quests"][:6]) + (f" (+{len(s['quests'])-6})" if len(s["quests"]) > 6 else "")
            lines.append(f"| {i} | {s['level_before']}->{s['level_after']} | {names} | {s['xp']} | {s['seconds']} | {s['total_seconds']/60:.1f} |")
        lines.append("")
    b, s = res["mit Buendeln"], res["ohne Buendel (je Quest einzeln)"]
    if b["level"] >= a.target_level and s["level"] >= a.target_level:
        lines.append(f"Vergleich: Buendel {b['seconds']/60:.0f} min, einzeln {s['seconds']/60:.0f} min "
                     f"({100*(1-b['seconds']/s['seconds']):.0f} % weniger).")
    skipped = [q for q in b["pool"] if q["id"] not in b["done"] and (q["required_level"] or 1) <= a.target_level]
    lines += ["", f"Nicht gemachte Quests (Mindestlevel <= {a.target_level}) bei Variante mit Buendeln: {len(skipped)} von {len(b['pool'])}"]
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "route_report.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
