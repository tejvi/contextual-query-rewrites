import unittest
from generate import Generator
import os
import shutil


class TestRawData(unittest.TestCase):
    def test_get_permutations(self):
        chunks = ['a']

        result = Generator("dummy_file",
                  "output.txt").get_permutations(chunks)

        expected = ['a <::::>', '<::::> a']

        self.assertEqual(expected, result)

    def test_write_pairs(self):
        chunks = ['a', 'b']

        result = Generator("dummy_file",
                  "output.txt").get_pairs(chunks)

        expected = [' a <::::> b ']

        self.assertEqual(expected, result)

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
