
import os
import sys


sys.path.append('./../utils/')
import preprocess_utils as preprocess
import translate_utils as translate



def main(inp_dir):
    inp_file_path = os.path.join(inp_dir, "train.tsv")

    preprocess.split(['<::::>', '\t'], inp_file_path, './split_train', chunk_size=20000)

    translate.translate_data('./split_train', 'outputs', src_lang='en', dst_lang='hi')

    preprocess.merge('outputs', 'train_hi.tsv')

    for file in ['dev.tsv', 'test.tsv']:
        inp_file_path = os.path.join(inp_dir, file)
        translate.translate_data(inp_file_path, file.split('.')[0] +'.tsv')

if  __name__ == '__main__':
    main(sys.argv[1])


