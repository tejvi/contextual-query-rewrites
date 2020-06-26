import os
import shutil
import unittest
import scrape_wiki as sc


class TestScraper(unittest.TestCase):
    def test_get_query_params(self):
        file = open("dummy_file.txt", 'w')
        test_res = sc.Scraper(
            "dummy_file.txt",
            "https://hi.wikipedia.org/w/api.php").get_query_params(
                ['1', '2', '3'])['titles']
        file.close()

        os.remove("dummy_file.txt")

        expected_res = "1|2|3"
        self.assertEqual(expected_res, test_res)

    def test_get_revision_ids(self):
        file = open("dummy_file.txt", 'w')
        test_res = sc.Scraper(
            "dummy_file.txt",
            "https://hi.wikipedia.org/w/api.php").get_revision_ids('कपूर')
        file.close()
        os.remove("dummy_file.txt")

        self.assertEqual({
            'revid': 1316759,
            'parentid': 1195685
        } in test_res, True)

    def test_get_diff(self):
        file = open("dummy_file.txt", 'w')
        test_res = sc.Scraper("dummy_file.txt",
                              "https://hi.wikipedia.org/w/api.php").get_diff(
                                  1316759, 1195685)
        file.close()
        os.remove("dummy_file.txt")
        self.assertEqual(test_res, ("{{taxobox", "{Name: CINNAMOMUM CAMPHORA"))

    def test_write_raw_data_chunk(self):

        file = open("dummy_file.txt", 'wb')
        file.write("कपूर".encode())
        file.close()

        sc.Scraper("dummy_file.txt",
                   "https://hi.wikipedia.org/w/api.php",
                   titles_per_chunk=1,
                   max_rev_ids=1).write_raw_data_chunk(0)

        os.remove("dummy_file.txt")
        self.assertTrue(os.path.exists("raw_data/raw_data_0_1.txt"))

    def test_write_raw_data(self):
        file = open("dummy_file1.txt", 'wb')
        file.write("कपूर\n".encode())
        file.write("कपूर\n".encode())
        file.close()

        sc.Scraper("dummy_file1.txt",
                   "https://hi.wikipedia.org/w/api.php",
                   output_dir="./test_raw_dir/",
                   titles_per_chunk=1,
                   max_rev_ids=1).write_raw_data()

        os.remove("dummy_file1.txt")
        

        self.assertTrue(os.path.exists("./test_raw_dir/raw_data_0_1.txt") \
             and os.path.exists("./test_raw_dir/raw_data_1_2.txt"))
             
        shutil.rmtree('test_raw_dir')


if __name__ == '__main__':
    unittest.main()
