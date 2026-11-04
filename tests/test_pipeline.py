import csv
import os
import shutil
import tempfile
import unittest

from sma import claims
from sma.produce import PAUSES, parse_script, split_sentences

SCRIPT = """# Tiêu đề tập

<!-- ghi chú không đọc [C999] -->

## 1. Hook

Câu một. Câu hai có số 8 phút. [C001]

[PAUSE]

> ghi chú biên tập, không đọc

Đoạn hai. [C002]
"""


class TestParse(unittest.TestCase):
    def test_events(self):
        ev = parse_script(SCRIPT)
        self.assertEqual(ev[0], ("speech", "Tiêu đề tập", PAUSES["lead"]))
        texts = [e[1] for e in ev if e[0] == "speech"]
        self.assertNotIn("ghi chú biên tập, không đọc", " ".join(texts))
        self.assertNotIn("C999", " ".join(texts))
        self.assertIn(("pause", PAUSES["explicit"]), ev)
        self.assertEqual(ev[1][2], PAUSES["section"])  # first sentence after H1 + H2

    def test_split_keeps_all_text(self):
        par = " ".join(f"Câu số {i} khá dài để kiểm tra việc gộp nhóm câu." for i in range(20))
        groups = split_sentences(par)
        self.assertEqual(" ".join(groups), par)
        self.assertTrue(all(len(g) <= 260 for g in groups))


class TestClaims(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        with open(os.path.join(self.d, "script.md"), "w") as f:
            f.write(SCRIPT)
        with open(os.path.join(self.d, "sources.md"), "w") as f:
            f.write("| S01 | x |\n")

    def tearDown(self):
        shutil.rmtree(self.d)

    def write(self, rows):
        with open(os.path.join(self.d, "claims.csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(claims.COLUMNS)
            w.writerows(rows)

    def row(self, cid, cat="OBSERVED", src="S01", status="APPROVED"):
        return [cid, "x", cat, "standard", src, "", "loc", "high", "", "", status, ""]

    def test_ok(self):
        self.write([self.row("C001"), self.row("C002", cat="ANALOGY", src="")])
        self.assertEqual(claims.validate(self.d, release=True)[0], [])

    def test_failures(self):
        self.write([self.row("C001", src="S99"), self.row("C003", status="PENDING")])
        errs = " | ".join(claims.validate(self.d, release=True)[0])
        self.assertIn("S99 not defined", errs)
        self.assertIn("[C002] missing", errs)
        self.assertIn("C003 never tagged", errs)
        self.assertIn("PENDING blocks release", errs)

    def test_sourced_category_requires_source(self):
        self.write([self.row("C001", src=""), self.row("C002")])
        self.assertTrue(any("needs source_ids" in e for e in claims.validate(self.d)[0]))


if __name__ == "__main__":
    unittest.main()


class TestMarkupLeak(unittest.TestCase):
    def test_literal_comment_marker_inside_comment_is_caught(self):
        import tempfile, json, os, shutil
        from sma import produce
        d = tempfile.mkdtemp()
        try:
            with open(os.path.join(d, "script.md"), "w") as f:
                f.write("# T\n\n<!-- note with <!-- --> inside -->\n\nCâu đọc.\n")
            with open(os.path.join(d, "pronunciation.json"), "w") as f:
                json.dump({"entries": []}, f)
            with self.assertRaises(SystemExit):
                produce.plan(d, "piper-vais1000")
        finally:
            shutil.rmtree(d)


class TestPauseStacking(unittest.TestCase):
    def test_pause_then_section_does_not_stack(self):
        ev = parse_script("# T\n\nCâu một.\n\n[PAUSE]\n\n## 2. Next\n\nCâu hai.\n")
        self.assertEqual(ev[-2], ("pause", PAUSES["explicit"]))
        self.assertEqual(ev[-1][2], 0)  # no extra section gap after an explicit pause
