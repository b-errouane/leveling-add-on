"""Stufe 2: Normalisieren.

Liest die zusammengefuehrten Forever-Daten von QuestieDB (Export), die Quest-XP- und
Drop-Tabellen aus den QuestieDB-Support-Daten und die Client-Tabelle QuestXP (wago.tools)
und schreibt ein einheitliches JSON-Zwischenformat nach data/normalized/.

Jeder Datensatz traegt seine Herkunft in `source`. Aufruf (vom Repo-Root):
    python -I -m pipeline.normalize.normalize
"""
import csv
import json
import re
from datetime import date
from pathlib import Path

from pipeline.common.luatable import LuaParser

ROOT = Path(__file__).resolve().parents[2]
QDB = ROOT / "data/raw/QuestieDB"
COMBINED = QDB / "src/corrections/Forever/combined"
SUPPORT = QDB / "support/Forever"
WAGO = ROOT / "data/raw/wago"
OUT = ROOT / "data/normalized"

ROW = re.compile(r"^(\w+)\[(\d+)\]=(.*)$")
PLACEHOLDER = re.compile(r"<NYI>|<TXT>|\[DEPRECATED\]|\(DEPRECATED\)|\bUNUSED\b|^DEPRECATED|^ZZ", re.I)


def to_py(v):
    """Lua-Tabelle (dict mit Int-Schluesseln ab 1) -> Liste mit None-Luecken, sonst dict."""
    if isinstance(v, dict):
        if v and all(isinstance(k, int) and k > 0 for k in v):
            n = max(v)
            if n <= 4 * len(v) + 8:  # echte Positionsliste, kein duennes Zonen-Mapping
                return [to_py(v.get(i)) for i in range(1, n + 1)]
        return {str(k): to_py(x) for k, x in v.items()}
    return v


def ids(v):
    """Liste von IDs, ohne Luecken und ohne None."""
    v = to_py(v)
    return [x for x in v if isinstance(x, int)] if isinstance(v, list) else []


def coord_map(v):
    """spawns/waypoints: {zoneId: [[x, y], ...]} -> {int: [[x, y], ...]}"""
    out = {}
    if isinstance(v, dict):
        for zone, pts in v.items():
            pts = to_py(pts)
            if isinstance(pts, list):
                out[int(zone)] = [p for p in (to_py(q) for q in pts) if isinstance(p, list)]
    return out


def load_keys(path):
    keys = {}
    for ln in open(path, encoding="utf-8"):
        m = re.match(r"-- \[(\d+)\] = (\w+)", ln)
        if m:
            keys[m.group(2)] = int(m.group(1))
    return keys


def load_combined(kind):
    path = COMBINED / f"forever{kind}DB.lua"
    keys = load_keys(path)
    rows = {}
    for ln in open(path, encoding="utf-8"):
        m = ROW.match(ln.rstrip("\n"))
        if m:
            rows[int(m.group(2))] = LuaParser(m.group(3)).parse_table()
    return keys, rows


def lua_block(path, var):
    text = open(path, encoding="utf-8").read()
    m = re.search(re.escape(var) + r"\s*=\s*\[\[return ", text)
    p = LuaParser(text)
    p.i = m.end()
    return p.parse_table()


def objective_list(v):
    """[{id, text}] aus {{id, text, icon}, ...}"""
    out = []
    for o in (to_py(v) or []):
        if isinstance(o, list) and o and isinstance(o[0], int):
            out.append({"id": o[0], "text": o[1] if len(o) > 1 else None})
    return out


def kill_credit_list(v):
    out = []
    for o in (to_py(v) or []):
        if isinstance(o, list) and o and isinstance(o[0], list):
            out.append({"ids": [x for x in o[0] if isinstance(x, int)],
                        "base": o[1] if len(o) > 1 else None,
                        "text": o[2] if len(o) > 2 else None})
    return out


def trigger_end(v):
    """Erkundungsziel: {text, {zoneId: [[x, y], ...]}} -> {"text": str|None, "spawns": {zone: [[x, y]]}}"""
    if not isinstance(v, dict):
        return None
    text = v.get(1)
    return {"text": text if isinstance(text, str) else None,
            "spawns": {str(z): p for z, p in coord_map(v.get(2)).items()}}


def normalize_quests(keys, rows, xp_support, xp_table):
    g = lambda r, k: r.get(keys[k]) if k in keys else None
    out = {}
    for qid, r in rows.items():
        started = to_py(g(r, "startedBy")) or []
        finished = to_py(g(r, "finishedBy")) or []
        obj = to_py(g(r, "objectives")) or []
        obj += [None] * (6 - len(obj))
        rep = to_py(g(r, "reputationReward"))
        name = g(r, "name") or ""
        xp = None
        if qid in xp_support:
            lvl, val = xp_support[qid]
            xp = {"level": lvl, "xp": val, "source": "questie-support-classic"}
        out[str(qid)] = {
            "id": qid,
            "name": name,
            "placeholder": bool(PLACEHOLDER.search(name)),
            "required_level": g(r, "requiredLevel"),
            "quest_level": g(r, "questLevel"),
            "required_races": g(r, "requiredRaces"),
            "required_classes": g(r, "requiredClasses"),
            "zone_or_sort": g(r, "zoneOrSort"),
            "started_by": {"npc": ids(started[0]) if len(started) > 0 else [],
                           "object": ids(started[1]) if len(started) > 1 else [],
                           "item": ids(started[2]) if len(started) > 2 else []},
            "finished_by": {"npc": ids(finished[0]) if len(finished) > 0 else [],
                            "object": ids(finished[1]) if len(finished) > 1 else []},
            "objectives": {
                "creature": objective_list(obj[0]),
                "object": objective_list(obj[1]),
                "item": objective_list(obj[2]),
                "kill_credit": kill_credit_list(obj[4]),
                "has_reputation": bool(obj[3]),
                "has_spell": bool(obj[5]),
            },
            "objectives_text": [t for t in (to_py(g(r, "objectivesText")) or []) if t],
            "trigger_end": trigger_end(g(r, "triggerEnd")),
            "source_item": g(r, "sourceItemId"),
            "prequest_group": ids(g(r, "preQuestGroup")),
            "prequest_single": ids(g(r, "preQuestSingle")),
            "child_quests": ids(g(r, "childQuests")),
            "in_group_with": ids(g(r, "inGroupWith")),
            "exclusive_to": ids(g(r, "exclusiveTo")),
            "next_in_chain": g(r, "nextQuestInChain"),
            "parent_quest": g(r, "parentQuest"),
            "required_skill": to_py(g(r, "requiredSkill")),
            "required_min_rep": to_py(g(r, "requiredMinRep")),
            "quest_flags": g(r, "questFlags"),
            "special_flags": g(r, "specialFlags"),
            "reputation_reward": rep,
            "xp": xp,
            "source": ["questie-forever-combined"] + (["questie-support-classic"] if xp else []),
        }
    return out


def normalize_npcs(keys, rows):
    g = lambda r, k: r.get(keys[k]) if k in keys else None
    out = {}
    for nid, r in rows.items():
        out[str(nid)] = {
            "id": nid, "name": g(r, "name"),
            "min_level": g(r, "minLevel"), "max_level": g(r, "maxLevel"),
            "rank": g(r, "rank"), "zone_id": g(r, "zoneID"), "sub_name": g(r, "subName"),
            "spawns": {str(z): p for z, p in coord_map(g(r, "spawns")).items()},
            "quest_starts": ids(g(r, "questStarts")), "quest_ends": ids(g(r, "questEnds")),
            "faction_id": g(r, "factionID"), "npc_flags": g(r, "npcFlags"),
            "source": ["questie-forever-combined"],
        }
    return out


def normalize_objects(keys, rows):
    g = lambda r, k: r.get(keys[k]) if k in keys else None
    out = {}
    for oid, r in rows.items():
        out[str(oid)] = {
            "id": oid, "name": g(r, "name"), "zone_id": g(r, "zoneID"),
            "spawns": {str(z): p for z, p in coord_map(g(r, "spawns")).items()},
            "quest_starts": ids(g(r, "questStarts")), "quest_ends": ids(g(r, "questEnds")),
            "source": ["questie-forever-combined"],
        }
    return out


def normalize_items(keys, rows):
    g = lambda r, k: r.get(keys[k]) if k in keys else None
    out = {}
    for iid, r in rows.items():
        out[str(iid)] = {
            "id": iid, "name": g(r, "name"),
            "npc_drops": ids(g(r, "npcDrops")), "object_drops": ids(g(r, "objectDrops")),
            "start_quest": g(r, "startQuest"), "item_level": g(r, "itemLevel"),
            "required_level": g(r, "requiredLevel"),
            "vendors": ids(g(r, "vendors")),
            "source": ["questie-forever-combined"],
        }
    return out


def load_drops():
    raw = lua_block(SUPPORT / "DropTables/classicItemDrops.lua", "wowheadData")
    return {str(item): {str(npc): rate for npc, rate in v.items() if isinstance(rate, (int, float))}
            for item, v in raw.items() if isinstance(v, dict)}


def load_xp_support():
    text = open(SUPPORT / "QuestXP/xpDB-classic.lua", encoding="utf-8").read()
    return {int(a): (int(b), int(c)) for a, b, c in
            re.findall(r"^\s*\[(\d+)\]\s*=\s*\{(\d+),\s*(\d+)\}", text, re.M)}


def load_quest_xp_table():
    with open(WAGO / "QuestXP.csv", encoding="utf-8", newline="") as f:
        return {int(r["ID"]): [int(r[f"Difficulty_{i}"]) for i in range(10)] for r in csv.DictReader(f)}


def write(name, obj):
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / name, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    print(f"  {name}: {len(obj)} Eintraege")


def main():
    print("Normalisiere ...")
    qk, qrows = load_combined("Quest")
    nk, nrows = load_combined("Npc")
    ik, irows = load_combined("Item")
    ok, orows = load_combined("Object")
    xp_support = load_xp_support()
    xp_table = load_quest_xp_table()
    write("quests.json", normalize_quests(qk, qrows, xp_support, xp_table))
    write("npcs.json", normalize_npcs(nk, nrows))
    write("objects.json", normalize_objects(ok, orows))
    write("items.json", normalize_items(ik, irows))
    write("drops.json", load_drops())
    write("quest_xp_table.json", {str(k): v for k, v in xp_table.items()})
    meta = {
        "created": date.today().isoformat(),
        "inputs": {
            "questie_forever_combined": "data/raw/QuestieDB/src/corrections/Forever/combined (Export mit --include-authored)",
            "questie_support": "data/raw/QuestieDB/support/Forever (QuestXP/xpDB-classic.lua, DropTables/classicItemDrops.lua)",
            "wago_quest_xp": "data/raw/wago/QuestXP.csv, Produkt wowf, Build 1.60.1.70862",
        },
        "counts": {"quests": len(qrows), "npcs": len(nrows), "items": len(irows), "objects": len(orows)},
        "attribution": "Daten: QuestieDB (GPL-3.0), Wowhead-basierte Drop-Tabelle von Questie, Blizzard-Client-Tabellen via wago.tools. ForeverDB-Daten sind (noch) nicht enthalten.",
    }
    write("meta.json", meta)


if __name__ == "__main__":
    main()
