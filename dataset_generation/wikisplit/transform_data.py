import os
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class RawData:
    def __init__(self,
                 input_dir="./raw_data",
                 output_file="output.tsv",
                 sentence_boundary_char='।'):
        """
        RawData class is used for cleaning and transforming the raw data collected 
        into a tsv file that can be fed to lasertagger.
        input_dir : where the colleted data files are
        output_file : where the final data should be written to
        sentence_boundary_char : the sentence boundary character for the language 
        """
        self.input_dir_ = input_dir
        self.sentence_boundary_ = sentence_boundary_char
        self.output_file_ = output_file

    def clean_initial(self, raw_line):
        """
        some preliminary cleaning of the data obtained by webscraping.
        the cleaning is not exhaustive since most of the data gets discarded in the further steps.

        Lines without the corresponding added and deleted lines are discarded
        References are removed, along with stray formatting tags.

        warning: the api returns data in slightly different formats for 
        wikipedias of different languages.
        """

        braces_counter = 0
        brackets_counter = 0
        ref_flag = 0
        or_flag = 0

        if "<::::>" not in raw_line:
            return ""

        cleaned_string = ""
        i = 0
        while i < len(raw_line):

            if raw_line[i] == '{':
                braces_counter += 1

            elif raw_line[i] == '}':
                or_flag = 0
                braces_counter -= 1

            elif raw_line[i] == '[':
                brackets_counter += 1

            elif raw_line[i] == ']':
                or_flag = 0
                brackets_counter -= 1

            elif raw_line[i] == '|':
                or_flag = 1

            elif raw_line[i:].startswith("&lt;ref&gt;"):
                ref_flag = 1
                i += len("&lt;ref&gt;")

            elif raw_line[i:].startswith("&lt;ref"):
                ref_flag = 1
                i += len("&lt;ref")

            elif raw_line[i:].startswith("&lt;/ref&gt;"):
                ref_flag = 0
                i += len("&lt;/ref&gt;") - 1

            elif raw_line[i:].startswith("&gt;।"):
                ref_flag = 0
                i += len("&gt;।") - 1

            elif raw_line[i:].startswith("&gt;"):
                ref_flag = 0
                i += len("&gt;") - 1

            elif braces_counter == 0:
                if not or_flag and not ref_flag:
                    cleaned_string += raw_line[i]

            i += 1

        cleaned_string = cleaned_string.replace('&lt;', '')
        return cleaned_string

    def get_plausible_lines(self, cleaned_lines):
        """
        Given a list of lines, only outputs the lines where the data on each side
        differs by only one or two extra sentences - these are the edited sentences.

        cleaned_lines is the output from initial cleaning
        """
        plausible = []

        for i in range(len(cleaned_lines)):
            if '<::::>' in cleaned_lines[i]:
                first, second = cleaned_lines[i].split('<::::>')
                first_count = first.count(self.sentence_boundary_)
                second_count = second.count(self.sentence_boundary_)

                if first_count and second_count and (
                    ((first_count - second_count) > 0 and
                     (first_count - second_count) < 3) or
                    ((second_count - first_count) > 0 and
                     (second_count - first_count) < 3)):
                    plausible.extend([cleaned_lines[i]])

        return plausible

    def trim_surrounding_sentences(self, cleaned_lines):
        """
        In the case where there are extra sentences on either side of the edited sentences,
        passing them to this function will remove them.
        """

        final = []

        for line in cleaned_lines:
            try:
                first, second = line.split('<::::>')
                sent1 = first.split(self.sentence_boundary_)
                sent2 = second.split(self.sentence_boundary_)

                start = 0
                while(start < min(len(sent1), len(sent2))  \
                    and sent1[start].strip() == sent2[start].strip()):
                    start += 1

                end = 0
                while(end <= min(len(sent1), len(sent2)) and sent1[len(sent1) - end - 1].strip()  \
                    == sent2[len(sent2) - end - 1].strip()):
                    end += 1

                new_fused = self.sentence_boundary_.join(
                    sent1[start:len(sent1) - end]) + self.sentence_boundary_
                new_split = self.sentence_boundary_.join(
                    sent2[start:len(sent2) - end]) + self.sentence_boundary_

                final.append(new_fused + " <::::> " + new_split)

            except Exception as error:
                logging.info("[FAILED] trimming {1}, {0}".format(error, line))

        return final

    def match_trigrams(self, plausible_lines):
        """
        as outlined in the wikisplit paper, to decide whether the edited sentences
        actually are an example of splitting/fusing of sentences, the trigram prefix of
        the first split sentence is matched with the trigram prefix of the fused sentence.
        Then, the trigram suffix of the fused sentence is matched with the trigram suffix 
        of the second split sentence. Finally, the trigram suffixes of the first and the second 
        split sentences should not match
        """
        suffix_matched = []

        for line in plausible_lines:
            fused = line.split('<::::>')[0]
            split = line.split('<::::>')[1]

            if fused.count(self.sentence_boundary_) == 2 \
                and split.count(self.sentence_boundary_) == 1:
                fused, split = split, fused

            if fused.count(self.sentence_boundary_) == 1 \
                and split.count(self.sentence_boundary_) == 2:
                # look at the trigram prefix and trigram suffix
                fused_prefix_list = list(
                    filter(lambda x: x != '', fused.split(' ')))[:3]
                split_prefix_list = list(
                    filter(lambda x: x != '', split.split(' ')))[:3]

                if fused_prefix_list == split_prefix_list:

                    fused_suffix_list = list(
                        filter(lambda x: x != '', fused.split(' ')))[-3:]
                    split_suffix_list = list(
                        filter(lambda x: x != '', split.split(' ')))[-3:]

                    if fused_suffix_list == split_suffix_list:
                        split1_suffix_list = list(
                            filter(
                                lambda x: x != '',
                                split.split(self.sentence_boundary_)[0].split(
                                    ' ')))[-3:]
                        split2_suffix_list = list(
                            filter(
                                lambda x: x != '',
                                split.split(self.sentence_boundary_)[1].split(
                                    ' ')))[-3:]

                        if split1_suffix_list != split2_suffix_list:
                            suffix_matched.append(line)

        return suffix_matched

    def make_dataset(self):
        """
        The data from the files in the input directory is read,
        cleaned, filtered and then transformed into a format that lasertagger can work with, 
        before being written to a single output tsv file
        """

        outfile = open(self.output_file_, 'wb')

        for file in os.listdir(self.input_dir_):

            file = open(os.path.join(self.input_dir_, file), 'r')
            content = file.readlines()
            file.close()

            cleaned = [self.clean_initial(line) for line in content]
            plausible_paragraphs = self.get_plausible_lines(cleaned)
            trimmed_paragraphs = self.trim_surrounding_sentences(
                plausible_paragraphs)
            matches = self.match_trigrams(trimmed_paragraphs)

            for line in matches:
                outfile.write("{0}\t{1} <::::> {2}\n".format(
                    line.split('<::::>')[1],
                    line.split('<::::>')[0].split(self.sentence_boundary_)[0] +
                    self.sentence_boundary_,
                    line.split('<::::>')[0].split(self.sentence_boundary_)[1] +
                    self.sentence_boundary_).encode())

        outfile.close()


if __name__ == '__main__':
    raw_data = RawData()
    raw_data.make_dataset()
