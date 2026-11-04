"""Run with the vieneu venv: .venv-vieneu/bin/python -m unittest tests.test_phoneme_override (skips otherwise).

Goes through the engine's real text normalizer, which lowercases and expands acronyms before phonemization."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
try:
    import vieneu.v3turbo as vt
    from sma.runners.vieneu_runner import install_phoneme_overrides
except ImportError:  # system python has no vieneu
    vt = None


@unittest.skipIf(vt is None, "vieneu not installed in this interpreter")
class TestPhonemeOverride(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.orig = staticmethod(vt.phonemize_text_with_emotions)
        cls.encode, cls.applied = install_phoneme_overrides([
            {"text": "LIGO", "phonemes": "<L>"}, {"text": "Jebel Irhoud", "phonemes": "<J>"},
            {"text": "DNA", "phonemes": "<D>"}, {"text": "Homo sapiens", "phonemes": "<H>"}])
        cls.encode = staticmethod(cls.encode)

    @classmethod
    def tearDownClass(cls):
        vt.phonemize_text_with_emotions = cls.orig

    def ph(self, text):
        """Same path as tts.infer: encode -> engine normalizer/chunker -> (patched) phonemizer."""
        chunks, _ = vt.normalize_to_chunks_v3_with_gaps(self.encode(text), max_chars=256)
        return " ".join(vt.phonemize_text_with_emotions(c) for c in chunks)

    def test_replaces_name_keeps_vietnamese(self):
        out = self.ph("Đó là LIGO.")
        self.assertTrue(out.endswith("<L>."), out)
        self.assertNotIn("qzx", out)

    def test_capitalised_and_acronym_names_survive_normalizer(self):
        self.applied.clear()
        out = self.ph("Trong DNA của Homo sapiens, và ở Jebel Irhoud, người ta tìm thấy xương.")
        for t in ("<D>", "<H>,", "<J>,"):
            self.assertIn(t, out)
        self.assertEqual(self.applied, {"DNA": 1, "Homo sapiens": 1, "Jebel Irhoud": 1})

    def test_no_name_is_identity(self):
        t = "Không có tên riêng nào ở đây."
        self.assertEqual(self.ph(t), self.orig(vt.normalize_to_chunks_v3_with_gaps(t, max_chars=256)[0][0]))

    def test_whole_word_only(self):
        self.assertNotIn("<L>", self.ph("Từ LIGOX không phải tên."))


if __name__ == "__main__":
    unittest.main()
