import unittest
import preprocess_translate_data
import os
import shutil


class TestRawData(unittest.TestCase):
    def test_split(self):
        file = open("dummy_file.txt", 'w')
        file.write(" a <::::> b \t x \n")
        file.close()

        preprocess_translate_data.split(['<::::>', '\t'], 'dummy_file.txt',
                               'dummy_output.txt')

        file = open("dummy_output.txt", 'r')
        data = file.readlines()
        file.close()

        os.remove("dummy_output.txt")
        os.remove("dummy_file.txt")

        expected = [' a \n', ' b \n', ' x \n']

        self.assertEqual(data, expected)

    def test_split_chunks(self):
        file = open("dummy_file.txt", 'w')
        file.write(" a <::::> b \t x \n")
        file.write(" a <::::> b \t x \n")
        file.close()

        preprocess_translate_data.split(['<::::>', '\t'],
                               'dummy_file.txt',
                               'dummy_output',
                               chunk_size=1)

        data = []
        for file in os.listdir('dummy_output'):
            file = open("dummy_output/" + file, 'r')
            data.extend(file.readlines())
            file.close()

        expected = [' a \n', ' b \n', ' x \n', ' a \n', ' b \n', ' x \n']

        os.remove("dummy_file.txt")

        self.assertEqual(data, expected)
        # self.assertTrue(len(os.listdir("dummy_output")), 2)

        shutil.rmtree("dummy_output")

    def test_merge_wikifuse(self):
        file = open("dummy_file.txt", 'w')
        data = [' a \n', ' b \n', ' x \n', ' a \n', ' b \n', ' x \n']
        [file.write(x) for x in data]
        file.close()

        preprocess_translate_data.merge_wikifuse('dummy_file.txt', 'dummy_output.txt')

        result = open("dummy_output.txt", 'r').readlines()

        expected = [' a \t b <::::> x \n', ' a \t b <::::> x \n']

        os.remove("dummy_output.txt")
        os.remove("dummy_file.txt")

        self.assertEqual(result, expected)

    def test_merge_wikifuse_chunks(self):
        os.mkdir("dummy_output")
        file1 = open("dummy_output/dummy_file1.txt", 'w')
        file2 = open("dummy_output/dummy_file2.txt", 'w')
        data = [' a \n', ' b \n', ' x \n', ' a \n', ' b \n', ' x \n']
        [file1.write(x) for x in data[:3]]
        [file2.write(x) for x in data[3:]]

        file1.close()
        file2.close()

        preprocess_translate_data.merge_wikifuse('dummy_output', 'dummy_output.txt')

        result = open("dummy_output.txt", 'r').readlines()

        expected = [' a \t b <::::> x \n', ' a \t b <::::> x \n']

        self.assertEqual(result, expected)

        os.remove("dummy_output.txt")


if __name__ == '__main__':
    unittest.main()
