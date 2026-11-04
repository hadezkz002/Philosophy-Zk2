import unittest

from sma.textnorm import apply_lexicon, normalize, read_int


class TestNumbers(unittest.TestCase):
    def test_small_numbers(self):
        cases = {0: "không", 5: "năm", 10: "mười", 15: "mười lăm", 21: "hai mươi mốt", 24: "hai mươi tư",
                 25: "hai mươi lăm", 105: "một trăm linh năm", 110: "một trăm mười", 499: "bốn trăm chín mươi chín"}
        for n, w in cases.items():
            self.assertEqual(read_int(n), w, n)

    def test_large_numbers(self):
        self.assertEqual(read_int(299792458),
                         "hai trăm chín mươi chín triệu bảy trăm chín mươi hai nghìn bốn trăm năm mươi tám")
        self.assertEqual(read_int(149597870700),
                         "một trăm bốn mươi chín tỷ năm trăm chín mươi bảy triệu tám trăm bảy mươi nghìn bảy trăm")
        self.assertEqual(read_int(2017), "hai nghìn không trăm mười bảy")
        self.assertEqual(read_int(1676), "một nghìn sáu trăm bảy mươi sáu")
        self.assertEqual(read_int(300000), "ba trăm nghìn")
        self.assertEqual(read_int(1000005), "một triệu không trăm linh năm")

    def test_vietnamese_separators(self):
        self.assertEqual(normalize("299.792.458 mét"),
                         "hai trăm chín mươi chín triệu bảy trăm chín mươi hai nghìn bốn trăm năm mươi tám mét")
        self.assertEqual(normalize("147,1 triệu km"), "một trăm bốn mươi bảy phẩy một triệu ki-lô-mét")
        self.assertEqual(normalize("4,5 tỷ"), "bốn phẩy năm tỷ")
        self.assertEqual(normalize("0,05"), "không phẩy không năm")

    def test_units(self):
        self.assertEqual(normalize("gần 300.000 km/s."), "gần ba trăm nghìn ki-lô-mét trên giây.")
        self.assertEqual(normalize("khoảng 30 km/s"), "khoảng ba mươi ki-lô-mét trên giây")
        self.assertEqual(normalize("5 MeV"), "năm triệu e-léc-trôn vôn")

    def test_time_expression(self):
        self.assertEqual(normalize("8 phút 19 giây"), "tám phút mười chín giây")


class TestMarkupAndLexicon(unittest.TestCase):
    def test_strips_claim_tags_and_quotes(self):
        self.assertEqual(normalize('Con số "8 phút 20 giây" là làm tròn. [C008]'),
                         "Con số tám phút hai mươi giây là làm tròn.")

    def test_lexicon_longest_match_and_boundaries(self):
        lex = [{"pattern": "không-thời gian", "replacement": "không thời gian"},
               {"pattern": "Newton", "replacement": "Niu-tơn"},
               {"pattern": "Newtonian", "replacement": "SHOULD-NOT-APPLY-PARTIAL"}]
        self.assertEqual(apply_lexicon("Newton và không-thời gian", lex), "Niu-tơn và không thời gian")
        self.assertEqual(apply_lexicon("Newtonx", lex), "Newtonx")

    def test_number_inside_word_untouched(self):
        self.assertEqual(normalize("GW170817"), "GW170817")


if __name__ == "__main__":
    unittest.main()
