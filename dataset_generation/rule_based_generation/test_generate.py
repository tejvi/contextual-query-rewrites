import unittest
from generate import Generator
import os
import shutil


class TestRawData(unittest.TestCase):
    def test_write_permutations(self):
        full_sentence = "a b c"
        chunks = ['a']

        Generator("dummy_file",
                  "output.txt").write_permutations(chunks, full_sentence)

        expected = [' a b c \t a <::::> \n', ' a b c \t <::::> a \n']

        result = open("output.txt", 'r').readlines()
        os.remove("output.txt")
        self.assertEqual(expected, result)

    def test_write_pairs(self):
        full_sentence = "a b c"
        chunks = ['a', 'b']

        Generator("dummy_file",
                  "output.txt").write_pairs(chunks, full_sentence)

        expected = ['a b c \t a <::::> b \n']

        result = open("output.txt", 'r').readlines()
        os.remove("output.txt")
        self.assertEqual(expected, result)

    def test_generate(self):

        Generator("test_file.conllu", "test_output.txt",
                  split="pairs").generate()

        file = open("test_output.txt", 'r')
        contents = file.readlines()
        file.close()

        print("contents: ", contents)
        expected = [
            'इसके अतिरिक्त गुग्गुल कुंड , भीम गुफा तथा भीमशिला भी दर्शनीय स्थल हैं । \t इसके अतिरिक्त स्थल <::::> गुग्गुल कुंड , भीम गुफा तथा भीमशिला भी स्थल \n',
            'इसके अतिरिक्त गुग्गुल कुंड , भीम गुफा तथा भीमशिला भी दर्शनीय स्थल हैं । \t इसके अतिरिक्त स्थल <::::> दर्शनीय स्थल \n',
            'इसके अतिरिक्त गुग्गुल कुंड , भीम गुफा तथा भीमशिला भी दर्शनीय स्थल हैं । \t गुग्गुल कुंड , भीम गुफा तथा भीमशिला भी स्थल <::::> दर्शनीय स्थल \n'
        ]

        os.remove("test_output.txt")
        self.assertEqual(expected, contents)


if __name__ == '__main__':
    unittest.main()
