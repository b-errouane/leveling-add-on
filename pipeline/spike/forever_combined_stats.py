"""Spike: coverage of the merged Forever data (QuestieDB export) vs Classic base."""
import re, sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from luatable import LuaParser, load_data_block

RAW = Path(__file__).resolve().parents[2] / "data/raw/QuestieDB"
COMB = RAW / "src/corrections/Forever/combined"
ROW = re.compile(r"^(\w+)\[(\d+)\]=(.*)$")


def load_keys(path):
    keys = {}
    for ln in open(path, encoding="utf-8"):
        m = re.match(r"-- \[(\d+)\] = (\w+)", ln)
        if m:
            keys[m.group(2)] = int(m.group(1))
    return keys


def load_combined(name):
    path = COMB / f"forever{name}DB.lua"
    keys = load_keys(path)
    rows = {}
    for ln in open(path, encoding="utf-8"):
        m = ROW.match(ln.rstrip("\n"))
        if m:
            p = LuaParser(m.group(3))
            rows[int(m.group(2))] = p.parse_table()
    return keys, rows


qk, quests = load_combined("Quest")
nk, npcs = load_combined("Npc")
ik, items = load_combined("Item")
ok_, objs = load_keys, None
classic = load_data_block(RAW / "data/Classic/classicQuestDB.lua", "questData")
print(f"Forever (zusammengefuehrt): {len(quests)} Quests | Classic-Basis: {len(classic)}")
new_ids = sorted(set(quests) - set(classic))
print(f"Neue Quest-IDs: {len(new_ids)} | in Classic aber nicht mehr in Forever: {len(set(classic)-set(quests))}")

g = lambda q, k: q.get(qk[k])
def has_npc_spawns(npc_id):
    n = npcs.get(npc_id)
    return bool(n and n.get(nk["spawns"]))
def starter_ids(q):
    s = g(q, "startedBy") or {}
    return [x for x in (s.get(1) or {}).values()]
def finisher_ids(q):
    s = g(q, "finishedBy") or {}
    return [x for x in (s.get(1) or {}).values()]

def report(ids, label):
    c = Counter(); n = len(ids)
    for i in ids:
        q = quests[i]
        c["name"] += bool(g(q, "name"))
        c["questLevel"] += bool(g(q, "questLevel"))
        c["requiredLevel"] += bool(g(q, "requiredLevel"))
        c["zone"] += bool(g(q, "zoneOrSort"))
        c["starter (NPC/Objekt/Item)"] += bool(g(q, "startedBy"))
        c["finisher (NPC/Objekt)"] += bool(g(q, "finishedBy"))
        c["objectives"] += bool(g(q, "objectives"))
        c["objectivesText"] += bool(g(q, "objectivesText"))
        c["vorquest"] += bool(g(q, "preQuestGroup") or g(q, "preQuestSingle"))
        st, fi = starter_ids(q), finisher_ids(q)
        c["starter-NPC mit Spawn"] += any(has_npc_spawns(x) for x in st)
        c["finisher-NPC mit Spawn"] += any(has_npc_spawns(x) for x in fi)
    print(f"\n[{label}] n={n}")
    for k, v in c.items():
        print(f"  {k:28s} {v:5d}  {100*v/max(n,1):5.1f}%")

report(sorted(classic), "Classic-Basis-IDs (in Forever)")
report(new_ids, "NEUE Forever-Quests")

def bands(ids):
    b = Counter()
    for i in ids:
        l = g(quests[i], "questLevel")
        b[(l // 10 * 10) if isinstance(l, int) and l > 0 else "?"] += 1
    return dict(sorted(b.items(), key=lambda x: str(x[0])))
print("\nNeue Quests je Level-Band:", bands(new_ids))
print("Alle Quests je Level-Band:", bands(list(quests)))
print("Beispiele neue Quests:", [(i, g(quests[i], "name"), g(quests[i], "questLevel")) for i in new_ids[:6]])
print("NPCs:", len(npcs), "| Items:", len(items))
