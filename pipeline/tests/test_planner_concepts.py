"""Tests fuer die Bausteine des Routenplaners (Ressourcen, Wegenetz, Gelegenheiten).

Aufruf vom Repo-Root: python -m unittest pipeline.tests.test_planner_concepts -v
Voraussetzung: data/normalized/ ist erzeugt (python -m pipeline.normalize.normalize).
Die Tests nutzen kleine Strahlbreiten und pruefen Eigenschaften, keine genauen Zeiten.
"""
import copy
import unittest

from pipeline.derive import planner
from pipeline.derive.planner import P, build_world, plan, trace
from pipeline.emit.emit_lua import lua_str


class PlannerConcepts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.params0 = copy.deepcopy(P)
        cls.w = build_world()

    def setUp(self):
        P.clear()
        P.update(copy.deepcopy(self.params0))
        w = self.w
        w.excluded = set()
        w.slots = int(P["quest_log_slots"])
        w.fl_nodes, w.fl_edges = {}, {}
        w.errands = []

    def test_questlog_slots_limit_open_quests(self):
        self.w.slots = 2
        end = plan(self.w, 4, 20, 20.0, single=False)
        self.assertIsNotNone(end)
        self.assertLessEqual(max(len(s.open) for s in trace(end)), 2)

    def test_hearth_chosen_only_when_ready_and_faster(self):
        w = self.w
        near_home = next(iter(w.inns.values()))  # ein Gastwirt in der Zone
        s = w.initial_state().clone(home=near_home)
        # Spieler weit weg von der Heimat, Ziel direkt bei der Heimat: Ruhestein ist schneller
        s_far = s.clone(pos=(5.0, 5.0), t=0.0, hearth_ready=0.0)
        dt, mode, upd = w.go(s_far, near_home)
        self.assertEqual(mode, "hearth")
        self.assertIn("hearth_ready", upd)
        # gleiche Lage, aber Abklingzeit laeuft noch: zu Fuss
        s_cd = s_far.clone(hearth_ready=3600.0)
        self.assertEqual(w.go(s_cd, near_home)[1], "walk")
        # Ziel liegt nahe am Spieler: kein Ruhestein
        s_near = s.clone(pos=near_home, hearth_ready=0.0)
        self.assertEqual(w.go(s_near, (near_home[0] + 1.0, near_home[1] + 1.0))[1], "walk")

    def test_hearth_needs_a_home_to_be_set_first(self):
        """Ohne gesetzte Heimat gibt es keinen Ruhestein-Weg. Danach muss 'Heimat setzen' vorher im Plan stehen."""
        w = self.w
        self.assertIsNone(w.home0, "Start-Heimat soll standardmaessig nicht gesetzt sein")
        s = w.initial_state()
        self.assertIsNone(s.home)
        dt, mode, _ = w.go(s.clone(pos=(5.0, 5.0)), next(iter(w.inns.values())))
        self.assertEqual(mode, "walk")
        end = plan(w, 5, 20, 20.0, single=False)
        self.assertIsNotNone(end)
        home_set = False
        for st in trace(end)[1:]:
            if st.rec[0] == "sethome":
                home_set = True
            if st.rec[6] == "hearth":
                self.assertTrue(home_set, "Ruhestein benutzt, bevor die Heimat gesetzt wurde")

    def test_known_flight_point_changes_the_route(self):
        """Gleiches Level, gleiche Quests, gleiche Position, aber anderer Flugpunkt-Zustand -> anderer Weg."""
        w = self.w
        w.fl_nodes = {1: (5.0, 5.0), 2: (95.0, 95.0)}
        w.fl_edges = {(1, 2): 60.0, (2, 1): 60.0}
        base = w.initial_state().clone(pos=(6.0, 6.0), home=None)
        dest = (94.0, 94.0)
        no_fp = w.go(base.clone(flights=frozenset()), dest)
        one_fp = w.go(base.clone(flights=frozenset({1})), dest)
        both = w.go(base.clone(flights=frozenset({1, 2})), dest)
        self.assertEqual(no_fp[1], "walk")
        self.assertEqual(one_fp[1], "walk")  # ein einzelner Punkt reicht nicht
        self.assertEqual(both[1], "flight")
        self.assertLess(both[0], no_fp[0])

    def test_grinding_alone_reaches_a_level(self):
        w = self.w
        w.excluded = {q["id"] for q in w.pool}  # keine Quest verfuegbar
        end = plan(w, 3, 20, 20.0, single=False)
        self.assertIsNotNone(end)
        kinds = {s.rec[0] for s in trace(end)[1:]}
        self.assertIn("grind", kinds)
        self.assertNotIn("accept", kinds)

    def test_errand_speeds_up_later_fights(self):
        P["errands"] = [copy.deepcopy(P["_errands_beispiel"])]
        w = build_world()
        self.assertTrue(w.errands, "Errand-NPC sollte in der Zone liegen")
        self.assertEqual(w.speed_mult(0), 1.0)
        self.assertLess(w.speed_mult(2), w.speed_mult(1))
        # Lehrer ist erst ab der ersten Stufe eine Option
        s = w.initial_state()
        acts_lvl1 = [n.act for n in planner.expand(w, s, False) if n.rec[0] == "errand"]
        self.assertEqual(acts_lvl1, [])
        s4 = s.clone(level=4)
        errands = [n for n in planner.expand(w, s4, False) if n.rec[0] == "errand"]
        self.assertTrue(errands)

    def test_trainer_errand_is_class_agnostic(self):
        """Kosten = Mittel der Wege zum jeweils naechsten Lehrer jeder Klasse, nicht ein fester Lehrer."""
        P["errands"] = [copy.deepcopy(P["_errands_beispiel"])]
        w = build_world()
        self.assertGreaterEqual(len(w.class_trainers), 5, "mehrere Klassen sollten Lehrer in der Zone haben")
        e = w.errands[0]
        self.assertIn("classes", e)
        s = w.initial_state().clone(level=4, home=None)
        per_class = [min(w.go(s, p)[0] for p in ps) for ps in e["classes"].values()]
        n = [x for x in planner.expand(w, s, False) if x.rec[0] == "errand"][0]
        walk_only = n.rec[2] - e["seconds"]
        self.assertAlmostEqual(walk_only, sum(per_class) / len(per_class), places=3)
        self.assertGreaterEqual(walk_only, min(per_class) - 1e-6)
        self.assertLessEqual(walk_only, max(per_class) + 1e-6)

    def test_lua_string_escaping(self):
        evil = 'a"b\\c\nd]]; os.execute("x") --'
        out = lua_str(evil)
        self.assertTrue(out.startswith('"') and out.endswith('"'))
        self.assertNotIn("\n", out)
        self.assertNotIn('"b', out.replace('\\"', ''))  # Anfuehrungszeichen sind maskiert

    @classmethod
    def tearDownClass(cls):
        P.clear()
        P.update(cls.params0)


if __name__ == "__main__":
    unittest.main()
