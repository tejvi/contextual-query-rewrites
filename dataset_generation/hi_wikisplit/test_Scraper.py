
import unittest
import Scraper as sc
import os
import shutil

class TestScraper(unittest.TestCase):

    def test_get_query_params(self):
        f = open("dummy_file.txt", 'w')
        test_res = sc.Scraper("dummy_file.txt").get_query_params(['1', '2', '3'])['titles']
        f.close()

        os.remove("dummy_file.txt")        
        
        expected_res = "1|2|3"
        self.assertEqual(expected_res, test_res)


    def test_get_revision_ids(self):
        f = open("dummy_file.txt", 'w')
        test_res = sc.Scraper("dummy_file.txt").get_revision_ids('कपूर')
        f.close()
        os.remove("dummy_file.txt") 

        self.assertEqual({'revid': 1316759, 'parentid': 1195685} in test_res, True)

    def test_get_diff(self):
        f = open("dummy_file.txt", 'w')
        test_res = sc.Scraper("dummy_file.txt").get_diff(1316759, 1195685)
        f.close()
        os.remove("dummy_file.txt") 
        self.assertEqual(test_res, ("{{taxobox", "{Name: CINNAMOMUM CAMPHORA"))

    def test_write_raw_data_chunk(self):

        f = open("dummy_file.txt", 'wb')
        f.write("कपूर".encode())
        f.close()

        test_res = sc.Scraper("dummy_file.txt", titles_per_chunk=1, max_rev_ids=1).write_raw_data_chunk(0)

        os.remove("dummy_file.txt") 
        self.assertTrue(os.path.exists("raw_data/raw_data_0_1.txt"))
    
    def test_write_raw_data(self):
        f = open("dummy_file1.txt", 'wb')
        f.write("कपूर\n".encode())
        f.write("कपूर\n".encode())     
        f.close()
        
        test_res = sc.Scraper("dummy_file1.txt", output_dir = "./test_raw_dir/",
                 titles_per_chunk=1, max_rev_ids=1).write_raw_data()

        os.remove("dummy_file1.txt") 
        shutil.rmtree('test_raw_dir')

        self.assertTrue(os.path.exists("./test_raw_dir/raw_data_0_1.txt") \
             and os.path.exists("./test_raw_dir/raw_data_1_2.txt"))

if __name__ == '__main__':
    unittest.main()