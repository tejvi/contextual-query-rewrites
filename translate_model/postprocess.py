import os
import sys
sys.path.append('./../utils')

import utils.preprocess_utils as preprocess
import utils.translate_utils as translate

with open(config_file) as json_file:
    config = json.load(json_file)

file = open(sys.argv[1], 'r')
outfile = open(sys.argv[1].split('.')[0] +'_hi_rewritten.tsv', 'wb')

for line in file.readlines():
    line = line.strip().split('\t')[1]
    if line != "":
            translated = translate_text(line, src_lang='en', dst_lang='hi', project_id=config["ProjectID"])
            outfile.write(translated.encode() + '\n'.encode())
outfile.close()
file.close()