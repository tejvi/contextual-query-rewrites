import sys
import nltk


def get_bleu_score_avg(filename):
    """
    Returns the average of the bleu scores
    The file format is the one followed
    in wikisplit prediction outputs:
    source1 <::::> source2 \t output \t reference
    """
    data = open(filename, 'r').readlines()

    lines = len(data)
    avg = 0

    for i in data:
        splits = i.split('\t')
        reference = splits[2].split()
        output = splits[1].split()

        bleu_score = nltk.translate.bleu_score.sentence_bleu([reference],
                                                             output)

        avg += bleu_score

    return avg / lines


if __name__ == '__main__':
    bleu_avg = get_bleu_score_avg(sys.argv[1])
    print("bleu avg: ", bleu_avg)
