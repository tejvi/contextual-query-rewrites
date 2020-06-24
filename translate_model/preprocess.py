import os
import json
import sys
sys.path.append('./../utils')

import utils.preprocess_utils as preprocess
import utils.translate_utils as translate

file = open(sys.argv[1], 'r')
outfile = open(sys.argv[1].split('.')[0] + '_translated.tsv', 'w')

with open(config_file) as json_file:
    config = json.load(json_file)

for line in file.readlines():
    line = line.strip()
    if line != "":
        try:
            translated = translate.translate_text(line, src_lang="hi", dst_lang="en", project_id=config["ProjectID"])
            line1, line2 = translated.replace('.', ' . ').replace('?', ' ? ').split('<::::>')
            outfile.write('.' + '\t' + line1 + ' <::::> ' + line2 + '\n')
        except Exception as e:
            print("failed", e, line)

outfile.close()
file.close()