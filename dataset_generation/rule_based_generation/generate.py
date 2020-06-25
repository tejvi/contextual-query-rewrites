import sys
import logging
from itertools import permutations
import conllu


class Generator:
    """
    Generates the dataset based on a set of rules
    """

    def __init__(self,
                 input_file,
                 output_file,
                 ignore_projections=None,
                 split="permutation"):
        """
        ignore projects specifies the dependency labels that
        will be ignored.

        split specifies how the chunks should be distributed 
        over the two sentences.
        permutation and pairs are the two options.
        permutation specifies that the chunks will be divided in 
        all possible ways.
        pairs specifies that the each split sentence will get a
        chunk.
        """
        self.input_ = input_file
        self.output_path_ = output_file

        if ignore_projections is None:
            ignore_projections = ['aux', 'punct', 'cop']

        self.ignore_projections_ = ignore_projections

        self.split_ = self.write_permutations
        if split == "pairs":
            self.split_ = self.write_pairs

    def write_permutations(self, chunks, full_sentence):
        """
         writes the permutations to the output file.
        """
        output = open(self.output_path_, 'wb')
        chunks.append('<::::>')

        for instance in permutations(chunks):
            output.write(" {0} \t {1} \n".format(
                full_sentence, " ".join(instance).strip()).encode())
        output.close()

    def write_pairs(self, chunks, full_sentence):
        """
        writes the pairs to the output file
        """
        output = open(self.output_path_, 'wb')

        for i in range(len(chunks)):
            for j in range(i + 1, len(chunks)):
                output.write("{0} \t {1} <::::> {2} \n".format(
                    full_sentence, chunks[i].strip(),
                    chunks[j].strip()).encode())
        output.close()

    def to_string_rec(self, tokens_to_add, token_list):
        """
        helper function to convert a dependency parse tree 
        to the string it represents
        """
        for token in tokens_to_add:
            self.to_string_rec(token.children, token_list)
            token_list.append((token.__dict__['token']['form'],
                               token.__dict__['token']['id']))

    def to_string(self, tokens_to_add, token_list):
        """
        function to convert a dependency parse tree
        to the string that it represents
        """
        self.to_string_rec(tokens_to_add, token_list)
        token_list = sorted(token_list, key=lambda x: x[1])

        words = [x[0] for x in token_list]
        sentence_chunk = " ".join(words)
        return sentence_chunk.strip()

    def generate(self):
        """
        generates the dataset and writes to the output file.
        output format: full_sentence \t split1 <::::> split2
        """
        i = 0

        for line in conllu.parse_tree_incr(open(self.input_, 'r')):
            chunks = []

            full_sentence = self.to_string(line.children, [
                (line.__dict__['token']['form'], line.__dict__['token']['id'])
            ]).strip()

            for child in line.children:

                if child.__dict__['token']['deprel'].lower(
                ) not in self.ignore_projections_:
                    chunks.append(
                        self.to_string(child.children,
                                       [(line.__dict__['token']['form'],
                                         line.__dict__['token']['id']),
                                        (child.__dict__['token']['form'],
                                         child.__dict__['token']['id'])]))

            self.split_(chunks, full_sentence)

            logging.info("[WROTE] : {0}th sentence ".format(i))
            i += 1

if __name__ == '__main__':
    Generator(sys.argv[1], sys.argv[2]).generate()
    