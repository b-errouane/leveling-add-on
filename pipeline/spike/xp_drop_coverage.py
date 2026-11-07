"""Spike: how much quest-XP and drop-rate data exists for Forever quests (QuestieDB support data)."""
import re, sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from luatable import LuaParser, load_data_block
import forever_combined_stats as fc  # reuses loaders (prints its own report)

SUP = fc.RAW / "support/Forever"
xp = {int(a): (int(b), int(c)) for a, b, c in
      re.findall(r"^\s*\[(\d+)\]\s*=\s*\{(\d+),\s*(\d+)\}", open(SUP / "QuestXP/xpDB-classic.lua", encoding="utf-8").read(), re.M)}
text = open(SUP / "DropTables/classicItemDrops.lua", encoding="utf-8").read()
m = re.search(r"wowheadData\s*=\s*\[\[return ", text)
p = LuaParser(text); p.i = m.end()
drops = p.parse_table()
print("\n=== XP/Drops ===")
print("Quests mit XP-Eintrag (xpDB-classic):", len(xp))
print("Items mit Drop-Tabelle (wowheadData):", len(drops), "| Eintraege gesamt:", sum(len(v) for v in drops.values()))

def cov(ids, label):
    n = len(ids)
    x = sum(1 for i in ids if i in xp)
    itemq = [i for i in ids if (fc.g(fc.quests[i], "objectives") or {}).get(3)]
    d_all = d_any = 0
    for i in itemq:
        items = [o[1] for o in (fc.g(fc.quests[i], "objectives")[3]).values() if isinstance(o, dict) and 1 in o]
        have = [it in drops for it in items]
        d_any += any(have); d_all += all(have)
    print(f"[{label}] n={n}: XP vorhanden {x} ({100*x/n:.1f}%) | Quests mit Item-Ziel {len(itemq)}: "
          f"alle Items mit Drop-Daten {d_all}, mindestens eins {d_any}")

cov(sorted(fc.classic), "Classic-Basis")
cov(fc.new_ids, "Neue Forever-Quests")

# Mob level coverage in NPC table
lv = sum(1 for n in fc.npcs.values() if n.get(fc.nk["minLevel"]) and n.get(fc.nk["maxLevel"]))
sp = sum(1 for n in fc.npcs.values() if n.get(fc.nk["spawns"]))
print(f"NPCs gesamt {len(fc.npcs)} | mit Level {lv} | mit Spawns {sp}")
# sanity: xp level equals questLevel?
diff = sum(1 for i, (lvl, _) in xp.items() if i in fc.quests and fc.g(fc.quests[i], "questLevel") not in (lvl, None))
print("XP-Level != questLevel bei", diff, "Quests (Aenderungen in Forever gegenueber Classic-XP-Tabelle?)")
