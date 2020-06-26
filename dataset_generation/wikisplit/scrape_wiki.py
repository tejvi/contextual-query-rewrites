import os
import sys
import shutil
import logging
import requests

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class Scraper:
    """
    Uses the wikimedia api to get the revision histories of the titles 
    provided in the title dump file.
    Format varies between wikipedia languages
    """
    def __init__(self,
                 titles_file,
                 url,
                 titles_per_chunk=1000,
                 output_dir='./raw_data/',
                 max_rev_ids=500,
                 start_from=0):
        """
        titles_file: title dump file
        url: url to scrape from
        titles_per_chunk: chunk size, data gets written in chunks
        output_dir: data chunks will be written to this directory
        max_rev_ids: gets at most the specified number of revisions for a page. 
                    500 is the upper limit
        start_from: starts scraping from the specified title (index in the title dump file)
        """
        self.titles_file_ = open(titles_file)
        self.titles_ = self.titles_file_.readlines()
        self.titles_file_.close()

        self.start_from_ = start_from

        self.titles_per_chunk_ = max(min(titles_per_chunk, 500), 0)

        self.output_dir_ = output_dir
        if os.path.isdir(self.output_dir_):
            if self.start_from_ == 0:
                shutil.rmtree(self.output_dir_)
                os.mkdir(self.output_dir_)
        else:
            os.mkdir(self.output_dir_)

        self.url_ = url
        self.max_rev_ids = max_rev_ids
        self.session_ = requests.Session()

    def get_query_params(self, titles):
        """
        returns the query parameters based on the titles given
        """
        params = {
            "action": "query",
            "prop": "revisions",
            "rvlimit": self.max_rev_ids,
            "titles": "|".join(titles),
            "rvprop": "ids",
            "rvslots": "main",
            "formatversion": "2",
            "format": "json"
        }

        return params

    def get_rev_id_params(self, from_rev_id, to_rev_id):
        """
        returns the query parameters based on the revision ids given
        """
        params = {
            "action": "compare",
            "fromrev": from_rev_id,
            "torev": to_rev_id,
            "formatversion": "2",
            "format": "json"
        }
        return params

    def get_revision_ids(self, title):
        """
        Given a title, returns the revision IDs for that title
        """
        logging.info("[FETCHING TITLE] {0}".format(title))

        revision_ids = []
        params = self.get_query_params([title])
        response = self.session_.get(url=self.url_, params=params)
        data = response.json()

        try:
            for page in data["query"]["pages"]:
                revision_ids.extend(page["revisions"])

            logging.info("[FOUND] added {0} to the list".format(
                len(revision_ids)))

            return revision_ids

        except Exception as error:
            logging.info(
                "[FAILED] fetching revision ids for {1} failed with : {0}".
                format(error, title))

    def get_diff(self, from_rev_id, to_rev_id):
        """
        returns the diff of the edits
        """
        params = self.get_rev_id_params(from_rev_id, to_rev_id)
        response = self.session_.get(url=self.url_, params=params)
        data = response.json()

        try:
            textdata = data["compare"]["body"] \
                            .replace('<ins class="diffchange diffchange-inline">', '') \
                            .replace('*', '') \
                            .replace('<ins>', '') \
                            .replace('</ins>', '') \
                            .replace('<del class="diffchange diffchange-inline">', '') \
                            .replace('</del>', '')

            added = textdata.split('<td class="diff-addedline">')[1] \
                            .split("</div>")[0] \
                            .replace('<div>', '')

            deleted = textdata.split('<td class="diff-deletedline">')[1] \
                            .split("</div>")[0] \
                            .replace('<div>', '')

            logging.info("[DIFF] successfully done on {1} and {0}".format(
                to_rev_id, from_rev_id))
            return (added, deleted)

        except Exception as error:
            logging.info(
                "[FAILED] could not get diff for revision IDs {1} and {0} : {2}"
                .format(to_rev_id, from_rev_id, error))
            return -1

    def write_raw_data_chunk(self, from_line):
        """
        writes a chunk of data, from the specified index
        """
        to_line = from_line + self.titles_per_chunk_

        output_file_path = os.path.join(
            self.output_dir_,
            "raw_data_{0}_{1}.txt".format(from_line, to_line))
        output_file = open(output_file_path, 'wb')

        for title in self.titles_[from_line:to_line]:
            try:
                revision_ids = self.get_revision_ids(title.strip())
                
                for rev_id_pair in revision_ids:
                    raw_data = self.get_diff(rev_id_pair['revid'],
                                             rev_id_pair['parentid'])

                    if raw_data != -1:
                        output_file.write("{0} <::::> {1} \n".format(
                            raw_data[0], raw_data[1]).encode())

            except Exception as error:
                logging.info(
                    "[FAILED] could not get revision IDs for {0} : {1}".format(
                        title, error))

        output_file.close()
        logging.info("[WROTE] data for {0} - {1} to {2}".format(
            from_line, to_line, output_file_path))

    def write_raw_data(self):
        """
        starts scraping, and writes the data chunks to the output directory
        """
        logging.info(
            "[STARTED] collected data will be written to {0}\n[FOUND] {1} titles"
            .format(self.output_dir_, len(self.titles_)))

        for i in range(self.start_from_, len(self.titles_),
                       self.titles_per_chunk_):
            self.write_raw_data_chunk(i)

        logging.info("[DONE] all raw data written to {0}".format(
            self.output_dir_))


if __name__ == '__main__':

    if len(sys.argv) < 3:
        print("please specify the path to the title dump file and the url")
        sys.exit()

    # scraping from the hindi wiki https://hi.wikipedia.org/w/api.php
    scraper = Scraper(sys.argv[1], sys.argv[2])
    scraper.write_raw_data()
