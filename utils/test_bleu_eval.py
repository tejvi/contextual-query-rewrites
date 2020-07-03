import os
import unittest
import bleu_eval


class TestBLEUEval(unittest.TestCase):

    def test_bleu_similar(self):
        file = open("dummy_file.txt", 'w')
        file.write("word \t word word word word \t word word word word \n")
        file.close()

        score = bleu_eval.get_bleu_score_avg("dummy_file.txt")

        print(score)

        self.assertEqual(score, 1)

        os.remove("dummy_file.txt")

    def test_bleu_dissimilar(self):
        file = open("dummy_file.txt", 'w')
        file.write("word \t word1 word1 word1 word1 \t word word word word \n")
        file.close()

        score = bleu_eval.get_bleu_score_avg("dummy_file.txt")

        print(score)

        self.assertEqual(score, 0)

        os.remove("dummy_file.txt")


if __name__ == '__main__':
    unittest.main()
