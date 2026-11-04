import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
CUR = json.load(open(os.path.join(ROOT, "curriculum", "curriculum.json"), encoding="utf-8"))
FIELDS = ["prerequisites", "learning_objectives", "key_concepts", "common_misconceptions", "references",
          "related_episodes", "assessment_questions"]


class TestCurriculum(unittest.TestCase):
    def test_fields_and_levels(self):
        ids = {t["topic_id"] for t in CUR["topics"]}
        self.assertEqual(len(ids), len(CUR["topics"]))
        for t in CUR["topics"]:
            for f in FIELDS:
                self.assertIn(f, t, t["topic_id"])
            for f in ("learning_objectives", "key_concepts", "references", "assessment_questions"):
                self.assertTrue(t[f], f"{t['topic_id']} empty {f}")
            for p in t["prerequisites"]:
                self.assertIn(p, ids, f"{t['topic_id']} unknown prerequisite {p}")
            for p in t.get("external_prerequisites", []):   # Science Media Academy topic ids, not in this repo
                self.assertNotIn(p, ids)
        for d in CUR["domains"]:
            levels = {t["level"] for t in CUR["topics"] if t["domain"] == d}
            self.assertEqual(levels, set(CUR["levels"]), f"{d} must span L0-L5")

    def test_prerequisite_graph_is_acyclic_and_level_monotone(self):
        by = {t["topic_id"]: t for t in CUR["topics"]}
        state = {}

        def visit(n):
            self.assertNotEqual(state.get(n), "active", f"cycle at {n}")
            if state.get(n) == "done":
                return
            state[n] = "active"
            for p in by[n]["prerequisites"]:
                self.assertLessEqual(by[p]["level"], by[n]["level"], f"{p} is above {n}")
                visit(p)
            state[n] = "done"
        for n in by:
            visit(n)


class TestEpisodes(unittest.TestCase):
    def test_metadata_links(self):
        schema = json.load(open(os.path.join(ROOT, "standards", "episode.schema.json"), encoding="utf-8"))
        ids = {t["topic_id"] for t in CUR["topics"]}
        eps = sorted(e for e in os.listdir(os.path.join(ROOT, "episodes")) if e.startswith("P"))
        self.assertIn("P001", eps)
        for e in eps:
            meta = json.load(open(os.path.join(ROOT, "episodes", e, "metadata.json"), encoding="utf-8"))
            self.assertEqual(meta["episode_id"], e)
            self.assertEqual(meta["domain"], "PHIL")
            self.assertIn(meta["domain"], schema["properties"]["domain"]["enum"])
            for t in meta["topic_ids"]:
                self.assertIn(t, ids)
            for k in ("script", "claims", "sources"):
                self.assertTrue(meta[k]["path"].startswith(f"episodes/{e}/"), k)
        linked = [t["topic_id"] for t in CUR["topics"] if "P001" in t["related_episodes"]]
        self.assertEqual(linked, ["PHIL-L0-01"])

    def test_claim_gate_knows_philosophy_labels_and_tags(self):
        from sma import claims
        for label in ("PRIMARY_TEXT", "INTERPRETATION", "ARGUMENT_RECONSTRUCTION", "MISATTRIBUTION", "NARRATOR_VIEW"):
            self.assertIn(label, claims.CATEGORIES)
        self.assertIn("NARRATOR_VIEW", claims.UNSOURCED_OK)
        self.assertNotIn("PRIMARY_TEXT", claims.UNSOURCED_OK)   # a quotation always needs its source
        self.assertEqual(claims.TAG.findall("Socrates [P001-C01]."), ["P001-C01"])
        self.assertEqual(claims.SOURCE_DEF.findall("| PS001 | Plato |"), ["PS001"])


if __name__ == "__main__":
    unittest.main()
