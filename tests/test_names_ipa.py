import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
from sma.names import ipa_to_engine  # noqa: E402


class IpaToEngine(unittest.TestCase):
    def test_matches_engine_notation(self):
        # targets are the engine's own G2P output for these English words
        self.assertEqual(ipa_to_engine("/ˈn(j)uː.tən/")[0], "nˈuːtən")
        self.assertEqual(ipa_to_engine("/ˈɡæ.mə/")[0], "ɡˈæmə")
        self.assertEqual(ipa_to_engine("/ˈæl.bɚt/")[0], "ˈælbɚt")
        self.assertEqual(ipa_to_engine("/ˈlusi/")[0], "lˈusi")

    def test_secondary_stress_and_rhotic(self):
        self.assertEqual(ipa_to_engine("/ˌhoʊmoʊ ˈseɪpi.ənz/")[0], "hˌoʊmoʊ sˈeɪpiənz")
        self.assertEqual(ipa_to_engine("niˈændərˌtɑːl")[0], "niˈændɚtˌɑːl")

    def test_r_by_language(self):
        self.assertEqual(ipa_to_engine("enˈri.ko ˈfeɾ.mi", "it")[0], "enɾˈiko fˈeɾmi")
        self.assertEqual(ipa_to_engine("/ˈpæɹɪs/")[0], "pˈæɹɪs")

    def test_approximations_reported(self):
        ph, approx = ipa_to_engine("ˈoːlə ˈʁœˀmɐ")
        self.assertEqual(ph, "ˈoːlə ɹˈɜmɐ")
        self.assertEqual(set(approx), {"ʁ", "ˀ", "œ"})
        # every vowel substitution is reported, not only diacritic clean-up (GPT QA B1)
        self.assertEqual(ipa_to_engine("ɝ ɒ ɨ"), ("ɜː ɑː ɪ", ["ɒ", "ɝ", "ɨ"]))



class CountSyllables(unittest.TestCase):
    def test_foreign_names_count_vowel_groups(self):
        from sma.produce import count_syllables
        self.assertEqual(count_syllables("Tên của loài ấy là Ardipithecus ramidus."), 5 + 5 + 3)
        self.assertEqual(count_syllables("Không có tên riêng nào ở đây."), 7)


if __name__ == "__main__":
    unittest.main()
