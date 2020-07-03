import os
import unittest
from generate import Generator


class TestRawData(unittest.TestCase):
    def test_get_permutations(self):
        chunks = ['a']

        result = Generator("dummy_file", "output.txt").get_permutations(chunks)

        expected = ['a <::::>', '<::::> a']

        self.assertEqual(expected, result)

    def test_get_pairs(self):
        chunks = ['a', 'b']

        result = Generator("dummy_file", "output.txt").get_pairs(chunks)

        expected = [' a <::::> b ']

        self.assertEqual(expected, result)

    def test_drop_words_pairs_all(self):
        chunks = ['a', 'b']

        result = Generator("dummy_file", "output.txt",
                           drop_words_percentage=1).get_pairs(chunks)

        print(result)
        expected = ['  <::::>  ']

        self.assertEqual(expected, result)

    def test_drop_words_permutations_all(self):
        chunks = ['a']

        result = Generator("dummy_file", "output.txt",
                           drop_words_percentage=1).get_permutations(chunks)

        expected = ['  <::::>  ', '  <::::>  ']

        self.assertEqual(expected, result)

    def test_drop_words_pairs_half(self):
        chunks = ['a', 'b']

        result = Generator("dummy_file",
                           "output.txt",
                           drop_words_percentage=0.5).get_pairs(chunks)

        first_sentence_words = len(result[0].split('<::::>')[0].split())

        self.assertEqual(first_sentence_words, 1)

    def test_generate(self):

        Generator("test_file.conllu", "test_output.txt",
                  split="pairs").generate()

        file = open("test_output.txt", 'r')
        contents = file.readlines()
        file.close()

        print("contents: ", contents)
        expected = [
            ' इसके अतिरिक्त गुग्गुल कुंड , भीम गुफा तथा भीमशिला भी दर्शनीय स्थल हैं । \t  इसके अतिरिक्त स्थल <::::> गुग्गुल कुंड , भीम गुफा तथा भीमशिला भी स्थल  \n',
            ' इसके अतिरिक्त गुग्गुल कुंड , भीम गुफा तथा भीमशिला भी दर्शनीय स्थल हैं । \t  इसके अतिरिक्त स्थल <::::> दर्शनीय स्थल  \n',
            ' इसके अतिरिक्त गुग्गुल कुंड , भीम गुफा तथा भीमशिला भी दर्शनीय स्थल हैं । \t  गुग्गुल कुंड , भीम गुफा तथा भीमशिला भी स्थल <::::> दर्शनीय स्थल  \n'
        ]

        os.remove("test_output.txt")
        self.assertEqual(expected, contents)


if __name__ == '__main__':
    unittest.main()
