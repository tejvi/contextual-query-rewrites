import os
import shutil
import unittest
from transform_data import RawData


class TestRawData(unittest.TestCase):
    def test_clean_initial(self):
        line = "a {{ ab c d}} a [b | we] &lt; b b [[c | c]] &gt; <::::> cde"
        expected_line = "a  a b   b b c   <::::> cde"
        cleaned_line = RawData().clean_initial(line)
        self.assertEqual(expected_line, cleaned_line)

    def test_get_plausible_lines(self):
        lines = ["a . b . c . <::::> c . b. x .", "x . y .<::::> y ."]
        result = RawData(sentence_boundary_char='.').get_plausible_lines(lines)

        self.assertEqual(result, ["x . y .<::::> y ."])

    def test_time_surrounding_sentences(self):

        lines = [
            "a . b . c . d . <::::> a . y . x . d .", "x . y .<::::> x . z ."
        ]

        result = RawData(
            sentence_boundary_char='.').trim_surrounding_sentences(lines)

        self.assertEqual(result,
                         [" b . c . <::::>  y . x .", " y . <::::>  z ."])

    def test_match_trigrams(self):
        lines = [
            "first word is this . second word is not this . <::::> first word is this but second word is not this .",
            " first word is this . second word is . <::::> first word is this but second word is not this .",
            " first word is this . second word is this . <::::> first word is this but second word is not this ."
        ]
        result = RawData(sentence_boundary_char='.').match_trigrams(lines)
        self.assertEqual(len(result), 1)

    def test_make_dataset(self):
        if os.path.isdir("test_dir"):
            shutil.rmtree("test_dir")
        os.mkdir("test_dir")

        file1 = open("test_dir/f1.txt", 'wb')
        file1.write(
            "first word is this . second word is not this . <::::> first word is this but second word is not this . \n"
            .encode())
        file1.close()

        file2 = open("test_dir/f2.txt", 'wb')
        file2.write(
            "first word is this . second word is . <::::> first word is this but second word is not this . \n"
            .encode())
        file2.write(
            " first word is this . second word is this . <::::> first word is this but second word is not this .\n"
            .encode())
        file2.close()

        RawData(input_dir="test_dir",
                output_file="test_file.tsv",
                sentence_boundary_char='.').make_dataset()

        output_file = open("test_file.tsv")
        output = output_file.readlines()
        output_file.close()
        os.remove("test_file.tsv")
        shutil.rmtree("test_dir")
        self.assertEqual(output, [
            '  first word is this but second word is not this .\tfirst word is this . <::::>  second word is not this .\n'
        ])


if __name__ == '__main__':
    unittest.main()
