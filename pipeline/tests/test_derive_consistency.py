"""Die Einzelquest-Bewertung (derive.py) und der Planer (route.needs) muessen dieselbe Mob-Quelle und damit
dieselben Mob-XP fuer Item-Ziele verwenden.

Aufruf vom Repo-Root: python -m unittest pipeline.tests.test_derive_consistency -v
"""
import unittest

from pipeline.derive.derive import P, evaluate, load, mob_base_xp, npc_level, typical_tier
from pipeline.derive.route import needs


class DeriveMatchesPlanner(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.quests, cls.npcs = load("quests.json"), load("npcs.json")
        cls.objects, cls.items = load("objects.json"), load("items.json")
        cls.drops, cls.table = load("drops.json"), load("quest_xp_table.json")
        cls.tier = typical_tier(cls.quests, cls.table)

    def test_single_item_quests_use_the_same_source_mob(self):
        checked = 0
        for q in self.quests.values():
            if q["placeholder"] or q["zone_or_sort"] not in (9, 12):
                continue
            objs = q["objectives"]
            if len(objs["item"]) != 1 or objs["creature"] or objs["object"]:
                continue
            nd = needs(q, self.npcs, self.objects, self.items, self.drops)
            if not nd["item_needs"]:
                continue
            level = q["quest_level"] or q["required_level"] or 1
            expected = 0.0
            for mob, k in nd["kills"].items():
                npc = self.npcs[str(mob)]
                ml = npc_level(npc, level)
                mult = P["elite_xp_multiplier"] if (npc["rank"] or 0) > 0 else 1.0
                expected += k * mob_base_xp(level, ml) * mult
            got = evaluate(q, self.npcs, self.objects, self.items, self.drops, self.table, self.tier, 12)["mob_xp"]
            self.assertAlmostEqual(got, round(expected), delta=2, msg=f"Quest {q['id']} {q['name']}")
            checked += 1
        self.assertGreater(checked, 5, "zu wenige Item-Quests geprueft")


if __name__ == "__main__":
    unittest.main()
