"""Stufe 4: Pruefen.

Liest data/normalized/*.json, fuehrt automatische Pruefungen aus und schreibt einen
Qualitaetsbericht nach data/reports/. Aufruf (vom Repo-Root):
    python -m pipeline.validate.validate [--zones 9,12]

Exit-Code 1, wenn harte Fehler gefunden wurden (z. B. Zyklen im Vorquest-Graphen).
"""
import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NORM = ROOT / "data/normalized"
REPORTS = ROOT / "data/reports"


def load(name):
    with open(NORM / name, encoding="utf-8") as f:
        return json.load(f)


def find_cycles(edges):
    """edges: {quest: [prereq,...]}. Gibt Quests zurueck, die in einem Zyklus liegen (Kahn)."""
    indeg = {q: 0 for q in edges}
    out = defaultdict(list)
    for q, pre in edges.items():
        for p in pre:
            if p in indeg:
                indeg[q] += 1
                out[p].append(q)
    queue = [q for q, d in indeg.items() if d == 0]
    seen = 0
    while queue:
        q = queue.pop()
        seen += 1
        for nxt in out[q]:
            indeg[nxt] -= 1
            if indeg[nxt] == 0:
                queue.append(nxt)
    return sorted(q for q, d in indeg.items() if d > 0)


def validate(quests, npcs, objects, items, xp_table):
    errors, warnings = [], []
    stats = Counter()
    placeholders = [q["id"] for q in quests.values() if q["placeholder"]]
    stats["placeholder"] = len(placeholders)

    missing = Counter()
    no_pos_start = no_pos_end = 0
    for q in quests.values():
        qid = q["id"]
        for nid in q["started_by"]["npc"]:
            if str(nid) not in npcs:
                missing["starter_npc"] += 1
        for oid in q["started_by"]["object"]:
            if str(oid) not in objects:
                missing["starter_object"] += 1
        for iid in q["started_by"]["item"]:
            if str(iid) not in items:
                missing["starter_item"] += 1
        for nid in q["finished_by"]["npc"]:
            if str(nid) not in npcs:
                missing["finisher_npc"] += 1
        for oid in q["finished_by"]["object"]:
            if str(oid) not in objects:
                missing["finisher_object"] += 1
        for o in q["objectives"]["creature"]:
            if str(o["id"]) not in npcs:
                missing["objective_creature"] += 1
        for o in q["objectives"]["object"]:
            if str(o["id"]) not in objects:
                missing["objective_object"] += 1
        for o in q["objectives"]["item"]:
            if str(o["id"]) not in items:
                missing["objective_item"] += 1
        for field in ("prequest_group", "prequest_single", "child_quests", "exclusive_to"):
            for other in q[field]:
                if str(other) not in quests:
                    missing["quest_ref:" + field] += 1
        # Position vorhanden?
        starters = [npcs.get(str(n)) for n in q["started_by"]["npc"]] + [objects.get(str(o)) for o in q["started_by"]["object"]]
        enders = [npcs.get(str(n)) for n in q["finished_by"]["npc"]] + [objects.get(str(o)) for o in q["finished_by"]["object"]]
        if starters and not any(s and s["spawns"] for s in starters):
            no_pos_start += 1
        if enders and not any(e and e["spawns"] for e in enders):
            no_pos_end += 1
        if not q["started_by"]["npc"] and not q["started_by"]["object"] and not q["started_by"]["item"]:
            stats["ohne_annahme"] += 1
        if not q["finished_by"]["npc"] and not q["finished_by"]["object"]:
            stats["ohne_abgabe"] += 1
        # Plausibilitaet Level
        rl, ql = q["required_level"], q["quest_level"]
        if isinstance(rl, int) and isinstance(ql, int) and ql > 0 and rl > ql:
            stats["required_level_ueber_quest_level"] += 1
        # Quest-XP gegen Client-Tabelle (Cross-Check zweier Quellen)
        if q["xp"]:
            row = xp_table.get(str(q["xp"]["level"]))
            if row is None:
                stats["xp_level_nicht_in_client_tabelle"] += 1
            elif q["xp"]["xp"] not in row:
                stats["xp_wert_nicht_in_client_zeile"] += 1
            else:
                stats["xp_wert_in_client_zeile"] += 1
            if isinstance(ql, int) and q["xp"]["level"] != ql:
                stats["xp_level_ungleich_quest_level"] += 1
    stats["starter_ohne_position"] = no_pos_start
    stats["finisher_ohne_position"] = no_pos_end
    for k, v in missing.items():
        warnings.append(f"Fehlende Referenzen: {k} = {v}")

    # Vorquest-Graph. Bereinigung: Selbstverweise entfernen (Datenfehler) und Kanten zwischen
    # sich gegenseitig ausschliessenden Quests ignorieren (Varianten derselben Kette).
    edges = {}
    self_refs = excl_edges = 0
    for k, q in quests.items():
        qid = int(k)
        keep = []
        for pre in q["prequest_single"] + q["prequest_group"]:
            if pre == qid:
                self_refs += 1
            elif pre in q["exclusive_to"] or qid in (quests.get(str(pre)) or {}).get("exclusive_to", []):
                excl_edges += 1
            else:
                keep.append(pre)
        edges[qid] = keep
    stats["vorquest_selbstverweise_entfernt"] = self_refs
    stats["vorquest_kanten_bei_exklusiven_ignoriert"] = excl_edges
    cyc = find_cycles(edges)
    if cyc:
        errors.append(f"Zyklen im Vorquest-Graphen (nach Bereinigung): {len(cyc)} Quests betroffen, z. B. {cyc[:10]}")
    stats["quests_im_zyklus"] = len(cyc)
    return errors, warnings, stats, placeholders


def zone_summary(quests, npcs, zones):
    """Quests, deren Zone in `zones` liegt (zone_or_sort > 0)."""
    sel = [q for q in quests.values() if q["zone_or_sort"] in zones and not q["placeholder"]]
    if not sel:
        return None
    levels = [q["quest_level"] for q in sel if isinstance(q["quest_level"], int)]
    xp = [q["xp"]["xp"] for q in sel if q["xp"]]
    return {
        "quests": len(sel),
        "mit_xp": len(xp),
        "level_min": min(levels) if levels else None,
        "level_max": max(levels) if levels else None,
        "xp_summe": sum(xp),
        "mit_ziel_kill": sum(1 for q in sel if q["objectives"]["creature"] or q["objectives"]["kill_credit"]),
        "mit_ziel_item": sum(1 for q in sel if q["objectives"]["item"]),
        "mit_vorquest": sum(1 for q in sel if q["prequest_single"] or q["prequest_group"]),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zones", default="9,12", help="Komma-getrennte Zonen-IDs (AreaTable) fuer den Zonenbericht")
    args = ap.parse_args()
    zones = {int(z) for z in args.zones.split(",")}

    quests, npcs, objects, items = load("quests.json"), load("npcs.json"), load("objects.json"), load("items.json")
    xp_table = load("quest_xp_table.json")
    meta = load("meta.json")
    errors, warnings, stats, placeholders = validate(quests, npcs, objects, items, xp_table)
    zs = zone_summary(quests, npcs, zones)

    REPORTS.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Qualitaetsbericht (Normalisierung und Pruefung)",
        "",
        f"Erzeugt aus `data/normalized/` (Stand {meta['created']}).",
        f"Quellen: {meta['attribution']}",
        "",
        f"Quests {len(quests)}, NPCs {len(npcs)}, Objekte {len(objects)}, Items {len(items)}.",
        "",
        "## Harte Fehler",
        *(["- " + e for e in errors] or ["- keine"]),
        "",
        "## Warnungen",
        *(["- " + w for w in warnings] or ["- keine"]),
        "",
        "## Kennzahlen",
        *[f"- {k}: {v}" for k, v in sorted(stats.items())],
        "",
        f"## Platzhalter-Quests ({len(placeholders)})",
        ", ".join(f"{i}:{quests[str(i)]['name']}" for i in placeholders[:25]) + (" ..." if len(placeholders) > 25 else ""),
        "",
        f"## Zonenbericht (Zonen {sorted(zones)})",
        json.dumps(zs, ensure_ascii=False, indent=2) if zs else "keine Quests gefunden",
        "",
    ]
    out = REPORTS / "validation_report.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    print(f"\nBericht: {out}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
