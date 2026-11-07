"""Spike: load QuestieDB Forever + Classic quest data and report coverage."""
import sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from luatable import load_data_block, load_keys

root = Path(__file__).resolve().parents[2] / "data/raw/QuestieDB/data"
fq = root / "Forever/foreverQuestDB.lua"
cq = root / "Classic/classicQuestDB.lua"
print("classic file exists:", cq.exists(), "| files:", sorted(p.name for p in (root/"Classic").glob("*.lua")))

keys = load_keys(fq, "questKeys")
fore = load_data_block(fq, "questData")
print("Forever quests:", len(fore))
clas = load_data_block(cq, "questData") if cq.exists() else {}
print("Classic quests:", len(clas))
new_ids = sorted(set(fore) - set(clas))
print("IDs only in Forever:", len(new_ids), "| only in Classic:", len(set(clas) - set(fore)))

def f(q, name):
    return q.get(keys[name])

def completeness(ids, label):
    c = Counter()
    for i in ids:
        q = fore[i]
        c["total"] += 1
        c["has_starter"] += bool(f(q, "startedBy"))
        c["has_finisher"] += bool(f(q, "finishedBy"))
        c["has_objectives"] += bool(f(q, "objectives"))
        c["has_objectivesText"] += bool(f(q, "objectivesText"))
        c["has_zone"] += bool(f(q, "zoneOrSort"))
        c["has_questLevel"] += bool(f(q, "questLevel"))
        c["has_prequest"] += bool(f(q, "preQuestGroup") or f(q, "preQuestSingle"))
    print(f"\n[{label}]")
    for k, v in c.items():
        print(f"  {k:20s} {v:6d}  {100*v/c['total']:5.1f}%")

completeness(list(fore), "alle Forever-Quests")
completeness(new_ids, "nur neue Forever-Quests (nicht in Classic)")

lv = Counter()
for i in fore:
    l = f(fore[i], "questLevel")
    if l: lv[(l // 10) * 10] += 1
print("\nQuests je Level-Band (questLevel):", dict(sorted(lv.items())))
nlv = Counter()
for i in new_ids:
    l = f(fore[i], "questLevel")
    if l: nlv[(l // 10) * 10] += 1
print("Neue Quests je Level-Band:", dict(sorted(nlv.items())))
print("Beispiele neue Quests:", [(i, f(fore[i], 'name'), f(fore[i], 'questLevel')) for i in new_ids[:8]])
print("Quest-Felder (Index->Name):", {v: k for k, v in keys.items()})
