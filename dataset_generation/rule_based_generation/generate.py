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

        self.split_ = self.get_permutations
        if split == "pairs":
            self.split_ = self.get_pairs

    def get_permutations(self, chunks):
        """
         returns the permutations of the chunks
        """
        permutations_list = []
        chunks.append('<::::>')

        for instance in permutations(chunks):
            permutations_list.append(" ".join(instance).strip())

        return permutations_list

    def get_pairs(self, chunks):
        """
        writes the pairs to the output file
        """
        pairs = []

        for i in range(len(chunks)):
            for j in range(i + 1, len(chunks)):
                pairs.append(" {0} <::::> {1} ".format(chunks[i].strip(),
                                                       chunks[j].strip()))

        return pairs

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
        output_file = open(self.output_path_, 'wb')

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

            splits = self.split_(chunks)

            [
                output_file.write(" {0} \t {1} \n".format(
                    full_sentence, split).encode()) for split in splits
            ]

            logging.info("[WROTE] : {0}th sentence ".format(i))
            i += 1
        output_file.close()

if __name__ == '__main__':
    Generator(sys.argv[1], sys.argv[2]).generate()
