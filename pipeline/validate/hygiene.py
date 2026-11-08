"""Daten-Hygiene: sucht auffaellige Eintraege in den normalisierten Daten (z. B. ein Flugmeister ohne Flugpunkt).

Ausgabe: data/reports/hygiene_report.md und data/normalized/suspects.json (Liste auffaelliger NPC-/Quest-IDs mit Grund).
Aufruf: python -m pipeline.validate.hygiene

Die Pruefungen markieren nur. Ob ein Eintrag falsch ist, entscheidet ein Mensch oder eine zweite Quelle.
Toleranzen unten sind Diagnosewerte fuer den Bericht, keine Regeln fuer die Planung.
"""
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NORM = ROOT / "data/normalized"
WAGO = ROOT / "data/raw/wago"
REPORTS = ROOT / "data/reports"
FLIGHT_SUBNAME = "Flight Master"
FLIGHT_BIT = 8  # Questie-Kodierung: Bit 8 = Flugmeister (Flag 11). Das Flag 8192 ist dort Stallmeister, nicht Flugmeister!


def is_flight_master(n):
    return n.get("sub_name") == FLIGHT_SUBNAME or bool((n["npc_flags"] or 0) & FLIGHT_BIT)
NODE_TOLERANCE_YD = 150.0  # Diagnose: so weit darf ein Flugmeister vom Flugpunkt entfernt sein


def load(name):
    with open(NORM / name, encoding="utf-8") as f:
        return json.load(f)


def zone_frames():
    """Zonen-ID (AreaID) -> Weltkoordinaten-Rahmen der Hauptkarte (aus UiMapAssignment)."""
    frames = {}
    with open(WAGO / "UiMapAssignment.csv", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            area = int(r["AreaID"])
            if area and r["OrderIndex"] == "0" and area not in frames:
                minx, miny, maxx, maxy = (float(r[k]) for k in ("Region_0", "Region_1", "Region_3", "Region_4"))
                frames[area] = {"minx": minx, "miny": miny, "maxx": maxx, "maxy": maxy, "map": int(r["MapID"]),
                                "uimap": int(r["UiMapID"]), "w": maxy - miny, "h": maxx - minx}
    return frames


def to_world(frame, x, y):
    """Karten-Prozent -> Weltkoordinaten (X, Y)."""
    return frame["maxx"] - y * frame["h"] / 100.0, frame["maxy"] - x * frame["w"] / 100.0


def taxi_nodes():
    with open(WAGO / "TaxiNodes.csv", encoding="utf-8", newline="") as f:
        return [{"id": int(r["ID"]), "name": r["Name_lang"], "x": float(r["Pos_0"]), "y": float(r["Pos_1"]),
                 "map": int(r["ContinentID"])} for r in csv.DictReader(f)]


def main():
    npcs, quests = load("npcs.json"), load("quests.json")
    frames, nodes = zone_frames(), taxi_nodes()
    suspects = defaultdict(list)
    sections = []

    # 1) Flugmeister ohne passenden Flugpunkt
    lines, nfm, nbad = [], 0, 0
    for n in npcs.values():
        if not is_flight_master(n):
            continue
        for zone, pts in n["spawns"].items():
            fr = frames.get(int(zone))
            if not fr or not pts:
                continue
            nfm += 1
            wx, wy = to_world(fr, pts[0][0], pts[0][1])
            dists = [(math.hypot(nd["x"] - wx, nd["y"] - wy), nd) for nd in nodes if nd["map"] == fr["map"]]
            d, nd = min(dists, key=lambda t: t[0]) if dists else (None, None)
            if d is None or d > NODE_TOLERANCE_YD:
                nbad += 1
                suspects[n["id"]].append("flight-master-without-taxinode")
                lines.append(f"- {n['id']} {n['name']} (Lvl {n['min_level']}) Zone {zone} bei {pts[0]}: naechster Flugpunkt "
                             f"{nd['name'] + ' in ' + str(round(d)) + ' yd' if nd else 'keiner'}")
    sections.append((f"Flugmeister ohne passenden Flugpunkt ({nbad} von {nfm} geprueften)", lines))

    # 2) Flugpunkte ohne Flugmeister im Rahmen (nur Information)
    lines = []
    for nd in nodes:
        for zone, fr in frames.items():
            if fr["map"] != nd["map"]:
                continue
            if not (fr["minx"] <= nd["x"] <= fr["maxx"] and fr["miny"] <= nd["y"] <= fr["maxy"]):
                continue
            fm = [n for n in npcs.values() if is_flight_master(n) and n["spawns"].get(str(zone))
                  and any(math.hypot(*(a - b for a, b in zip(to_world(fr, *p[:2]), (nd["x"], nd["y"])))) <= NODE_TOLERANCE_YD
                          for p in n["spawns"][str(zone)])]
            if not fm and nd["name"] and "World target" not in nd["name"] and "Generic" not in nd["name"]:
                lines.append(f"- Flugpunkt {nd['id']} {nd['name']} liegt in Zone {zone}, aber kein Flugmeister in der Naehe")
            break
    sections.append((f"Flugpunkte ohne Flugmeister ({len(lines)})", lines[:15]))

    # 3) Koordinaten ausserhalb 0..100 (die Platzhalter (-1, -1) von Questie zaehlen separat)
    lines, sentinel = [], 0
    for n in npcs.values():
        for zone, pts in n["spawns"].items():
            real = [p for p in pts if not (0 <= p[0] <= 100 and 0 <= p[1] <= 100) and p != [-1, -1]]
            sentinel += sum(1 for p in pts if p == [-1, -1])
            if real:
                suspects[n["id"]].append("coords-out-of-range")
                lines.append(f"- {n['id']} {n['name']} Zone {zone}: {real[:2]}")
    sections.append((f"Spawn-Koordinaten ausserhalb 0-100 ({len(lines)}); Platzhalter (-1, -1): {sentinel} Positionen (Instanzen/unbekannt)", lines[:30]))

    # 4) NPC-Level auffaellig
    lines = []
    for n in npcs.values():
        lo, hi = n["min_level"], n["max_level"]
        if isinstance(lo, int) and isinstance(hi, int) and (lo > hi or hi > 70 or (n["spawns"] and lo == 0 and hi == 0)):
            suspects[n["id"]].append("npc-level")
            lines.append(f"- {n['id']} {n['name']}: Level {lo}-{hi}")
    sections.append((f"NPC-Level auffaellig ({len(lines)})", lines[:30]))

    # 5) Quests: Level-Widersprueche und kaputte Verweise
    lines_lv, lines_ref = [], []
    for q in quests.values():
        if q["placeholder"]:
            continue
        rl, ql = q["required_level"], q["quest_level"]
        if isinstance(rl, int) and isinstance(ql, int) and ql > 0 and rl > ql:
            suspects[f"q{q['id']}"].append("required-level-above-quest-level")
            lines_lv.append(f"- {q['id']} {q['name']}: Mindestlevel {rl} > Questlevel {ql}")
        nxt = q["next_in_chain"]
        if nxt and str(nxt) not in quests:
            suspects[f"q{q['id']}"].append("next-in-chain-missing")
            lines_ref.append(f"- {q['id']} {q['name']}: naechste Quest {nxt} existiert nicht")
    sections.append((f"Quests mit Mindestlevel ueber Questlevel ({len(lines_lv)})", lines_lv[:40]))
    sections.append((f"Quests mit fehlender Folgequest ({len(lines_ref)})", lines_ref[:30]))

    # 6) Kill-Ziele ohne Position je Zone
    by_zone = defaultdict(lambda: [0, 0])
    for q in quests.values():
        if q["placeholder"] or not q["zone_or_sort"] or q["zone_or_sort"] < 0:
            continue
        for o in q["objectives"]["creature"]:
            npc = npcs.get(str(o["id"]))
            by_zone[q["zone_or_sort"]][0] += 1
            if not npc or not npc["spawns"]:
                by_zone[q["zone_or_sort"]][1] += 1
    worst = sorted(((z, t, m) for z, (t, m) in by_zone.items() if m), key=lambda x: -x[2])[:12]
    sections.append(("Kill-Ziele ohne bekannte Position (Zone: ohne Position / gesamt)",
                     [f"- Zone {z}: {m} / {t}" for z, t, m in worst]))

    # Bericht
    out = ["# Daten-Hygiene", "", "Markiert nur. Die Planung nutzt diese Hinweise nicht automatisch.", ""]
    for title, lines in sections:
        out += [f"## {title}", *(lines or ["- keine"]), ""]
    out += [f"Auffaellige Eintraege insgesamt: {len(suspects)} (siehe `data/normalized/suspects.json`)."]
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "hygiene_report.md").write_text("\n".join(out), encoding="utf-8")
    with open(NORM / "suspects.json", "w", encoding="utf-8") as f:
        json.dump({str(k): v for k, v in suspects.items()}, f, ensure_ascii=False, indent=1)
    print("\n".join(out)[:6000])


if __name__ == "__main__":
    main()
