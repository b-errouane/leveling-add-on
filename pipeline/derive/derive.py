"""Stufe 5 (Prototyp): Einzelquest-Bewertung (XP pro Stunde, allein betrachtet).

Eingabe: data/normalized/*.json, pipeline/config/params.json
Ausgabe: data/derived/quest_eval.json, data/reports/derived_report.md

Alle Zeitmodelle und Zonengroessen sind ANNAHMEN (siehe params.json) und werden spaeter kalibriert.
Aufruf: python -m pipeline.derive.derive [--zones 9,12] [--max-level 12]
"""
import argparse
import json
import math
import re
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NORM = ROOT / "data/normalized"
OUT = ROOT / "data/derived"
REPORTS = ROOT / "data/reports"
P = json.load(open(ROOT / "pipeline/config/params.json", encoding="utf-8"))


MAX_COUNT = 40  # groessere Zahlen im Zieltext sind meist keine Stueckzahlen (Geld, Level, Jahre)
UNKNOWN_TRAVEL_YARDS = 700.0  # Ersatzweg, wenn Annahme- oder Abgabeposition in dieser Zone fehlt


def load(n):
    with open(NORM / n, encoding="utf-8") as f:
        return json.load(f)


def mob_base_xp(player, mob):
    """Basis-Kill-XP. Bei gleichem Level 5*Level+45 (vom Wowhead-Rechner bestaetigt).
    Die Abhaengigkeit vom Level-Unterschied ist die Classic-Formel aus dem Gedaechtnis (ungeprueft)."""
    base = player * 5 + 45
    if mob >= player:
        return (base * (20 + min(mob - player, 4)) / 10 + 1) / 2
    if player <= 5:
        gray = 0
    elif player < 40:
        gray = player - 5 - player // 10
    elif player < 60:
        gray = player - 1 - player // 5
    else:
        gray = 51
    if mob <= gray:
        return 0.0
    zd = (5 if player <= 7 else 6 if player <= 9 else 7 if player <= 11 else 8 if player <= 15
          else 9 if player <= 19 else 11 if player <= 29 else 12 if player <= 39 else 13 if player <= 44
          else 14 if player <= 49 else 15 if player <= 54 else 16 if player <= 59 else 17)
    return base * (1 - (player - mob) / zd)


def centroid(points):
    if not points:
        return None
    return (sum(p[0] for p in points) / len(points), sum(p[1] for p in points) / len(points))


def pts(entity, zone):
    return [tuple(p) for p in (entity or {}).get("spawns", {}).get(str(zone), [])]


def yards(a, b, zone):
    if a is None or b is None:
        return None
    w, h = P["zone_size_yards"].get(str(zone), P["zone_size_yards"]["default"])
    return math.hypot((a[0] - b[0]) * w / 100.0, (a[1] - b[1]) * h / 100.0)


def counts_from_text(q):
    """Heuristik: Zahlen aus dem Zieltext der Reihe nach den Zielen zuordnen, sonst 1."""
    nums = [int(n) for t in q["objectives_text"] for n in re.findall(r"\b(\d{1,3})\b", t)]
    k = len(q["objectives"]["creature"]) + len(q["objectives"]["item"]) + len(q["objectives"]["object"])
    if k == 0:
        return [], "text"  # reine Liefer-/Gespraechsquest, keine Mengen noetig
    if len(nums) >= k:
        out, src = nums[:k], "text"
    elif nums:
        out, src = (nums + [nums[-1]] * k)[:k], "text-teilweise"
    else:
        out, src = [1] * k, "geraten"
    if any(n > MAX_COUNT for n in out):
        out, src = [n if n <= MAX_COUNT else 1 for n in out], "unplausibel-korrigiert"
    return out, src


def typical_tier(quests, table):
    """Typische Schwierigkeitsstufe (Spalte in QuestXP) aus Quests mit bekanntem XP."""
    tiers = []
    for q in quests.values():
        if q["xp"] and not q["placeholder"]:
            row = table.get(str(q["xp"]["level"]))
            if row and q["xp"]["xp"] in row:
                tiers.append(row.index(q["xp"]["xp"]))
    return int(statistics.median(tiers))


def first_point(ids, store, zone):
    for i in ids:
        c = centroid(pts(store.get(str(i)), zone))
        if c is not None:
            return c
    return None


def kill_seconds(elite):
    return P["seconds_per_kill"] + (P["elite_extra_seconds_per_kill"] if elite else 0.0)


def mob_gain(npc, level, count):
    ml = round(((npc["min_level"] or level) + (npc["max_level"] or level)) / 2)
    elite = (npc["rank"] or 0) > 0
    return count * mob_base_xp(level, ml) * (P["elite_xp_multiplier"] if elite else 1.0), elite


def evaluate(q, npcs, objects, items, drops, table, est_tier, zone):
    conf = []
    level = q["quest_level"] or q["required_level"] or 1  # Annahme: Spielerlevel = Quest-Level
    if q["xp"]:
        qxp, xp_src = q["xp"]["xp"], "bekannt"
    else:
        row = table.get(str(level))
        qxp, xp_src = (row[est_tier] if row else 0), "geschaetzt"
        conf.append("quest-xp geschaetzt")

    giver = first_point(q["started_by"]["npc"], npcs, zone) or first_point(q["started_by"]["object"], objects, zone)
    ender = first_point(q["finished_by"]["npc"], npcs, zone) or first_point(q["finished_by"]["object"], objects, zone)
    if giver is None or ender is None:
        conf.append("position unbekannt")

    counts, csrc = counts_from_text(q)
    if csrc != "text":
        conf.append("mengen " + csrc)
    idx = 0
    area_pts, kills, mob_xp, seconds_obj, any_elite = [], 0.0, 0.0, 0.0, False

    for o in q["objectives"]["creature"]:
        n = counts[idx] if idx < len(counts) else 1
        idx += 1
        npc = npcs.get(str(o["id"]))
        if not npc:
            conf.append("ziel-npc fehlt")
            continue
        area_pts += pts(npc, zone)
        gain, elite = mob_gain(npc, level, n)
        mob_xp += gain
        kills += n
        any_elite = any_elite or elite
        seconds_obj += n * kill_seconds(elite)

    for o in q["objectives"]["object"]:
        n = counts[idx] if idx < len(counts) else 1
        idx += 1
        area_pts += pts(objects.get(str(o["id"])), zone)
        seconds_obj += n * P["seconds_per_object_interaction"]

    for o in q["objectives"]["item"]:
        n = counts[idx] if idx < len(counts) else 1
        idx += 1
        it = items.get(str(o["id"])) or {}
        rates = drops.get(str(o["id"]), {})
        srcs = [(npcs.get(str(x)), rates.get(str(x))) for x in it.get("npc_drops", [])]
        srcs = [(npc, r) for npc, r in srcs if npc and pts(npc, zone)]
        rated = [(npc, r) for npc, r in srcs if r]
        if rated:
            best = max(r for _, r in rated) / 100.0
            use = [npc for npc, r in rated if r / 100.0 >= best * 0.5]
            rate = best
        elif srcs:
            use = [npc for npc, _ in srcs]
            rate = P["unknown_drop_rate"]
            conf.append("droprate geschaetzt")
        else:
            obj_src = [objects.get(str(x)) for x in it.get("object_drops", [])]
            obj_src = [ob for ob in obj_src if ob and pts(ob, zone)]
            if obj_src:
                area_pts += [p for ob in obj_src for p in pts(ob, zone)]
                seconds_obj += n * P["seconds_per_object_interaction"]
            else:
                conf.append("item-quelle unbekannt")
                seconds_obj += n * P["seconds_per_object_interaction"]
            continue
        area_pts += [p for npc in use for p in pts(npc, zone)]
        k = n / max(rate, 0.01)
        gain, elite = mob_gain(use[0], level, k)
        mob_xp += gain
        kills += k
        any_elite = any_elite or elite
        seconds_obj += k * kill_seconds(elite)

    trig = q.get("trigger_end")
    if trig:  # Erkundungsziel: Ort anlaufen (Zeit fuer das Betreten ist im Overhead enthalten)
        area_pts += [tuple(p) for p in trig["spawns"].get(str(zone), [])]
    area = centroid(area_pts)
    if giver is not None and ender is not None:
        if area is not None:
            travel = yards(giver, area, zone) + yards(area, ender, zone)
        else:
            travel = yards(giver, ender, zone)
    else:
        travel = UNKNOWN_TRAVEL_YARDS  # Position fehlt oder liegt ausserhalb dieser Zone
    seconds = travel / P["run_speed_yards_per_s"] + seconds_obj + P["seconds_overhead_per_quest"]
    return {
        "id": q["id"], "name": q["name"], "level": level,
        "quest_xp": qxp, "quest_xp_quelle": xp_src, "mob_xp": round(mob_xp), "kills": round(kills, 1),
        "travel_yards": round(travel), "seconds": round(seconds),
        "xp_per_hour": round((qxp + mob_xp) / seconds * 3600) if seconds else None,
        "elite": any_elite, "confidence": sorted(set(conf)),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zones", default="9,12")
    ap.add_argument("--max-level", type=int, default=12)
    a = ap.parse_args()
    zones = {int(z) for z in a.zones.split(",")}
    quests, npcs, objects, items = load("quests.json"), load("npcs.json"), load("objects.json"), load("items.json")
    drops, table = load("drops.json"), load("quest_xp_table.json")
    est_tier = typical_tier(quests, table)
    spawn_zone = 12  # Northshire (9) und Elwynn (12) liegen im Koordinatenraum von Zone 12
    sel = [q for q in quests.values() if q["zone_or_sort"] in zones and not q["placeholder"]
           and (q["quest_level"] or 0) <= a.max_level]
    res = [evaluate(q, npcs, objects, items, drops, table, est_tier, spawn_zone) for q in sel]
    OUT.mkdir(parents=True, exist_ok=True)
    json.dump(res, open(OUT / "quest_eval.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    ok = sorted([r for r in res if r["xp_per_hour"] is not None], key=lambda r: -r["xp_per_hour"])
    conf_n = {}
    for r in res:
        for c in r["confidence"] or ["ok"]:
            conf_n[c] = conf_n.get(c, 0) + 1
    head = ["| ID | Name | Lvl | Quest-XP | Mob-XP | Kills | Weg (yd) | Zeit (s) | XP/h | Hinweise |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    fmt = lambda r: (f"| {r['id']} | {r['name'][:32]} | {r['level']} | {r['quest_xp']} ({r['quest_xp_quelle'][0]}) | "
                     f"{r['mob_xp']} | {r['kills']} | {r['travel_yards']} | {r['seconds']} | {r['xp_per_hour']} | "
                     f"{', '.join(r['confidence'])} |")
    lines = [f"# Einzelquest-Bewertung (Prototyp, Zonen {sorted(zones)}, bis Level {a.max_level})", "",
             "ANNAHMEN: Zeitmodell und Zonengroesse aus `pipeline/config/params.json`, nicht gemessen. Spielerlevel = Quest-Level.",
             f"Quest-XP fuer Quests ohne Angabe geschaetzt mit Stufe {est_tier} (Median bekannter Quests).", "",
             f"Quests bewertet: {len(res)}", "", "## Konfidenz-Hinweise",
             *[f"- {k}: {v}" for k, v in sorted(conf_n.items())], "",
             "## Beste 15 nach XP/h (einzeln betrachtet)", *head, *[fmt(r) for r in ok[:15]], "",
             "## Schlechteste 15 nach XP/h", *head, *[fmt(r) for r in ok[-15:]], ""]
    if ok:
        v = [r["xp_per_hour"] for r in ok]
        lines.append(f"XP/h: Median {int(statistics.median(v))}, 90. Perzentil {v[int(len(v) * 0.1)]}, 10. Perzentil {v[int(len(v) * 0.9)]}")
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "derived_report.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
