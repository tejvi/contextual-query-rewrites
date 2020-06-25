import os
import sys
import json

sys.path.append('./../utils/')
import preprocess_utils as preprocess
import translate_utils as translate


"""
writes the translated fused sentences to a file,
from the output of the lasertagger model
"""
with open("config.json") as json_file:
    config = json.load(json_file)

file = open(sys.argv[1], 'r')
outfile = open(sys.argv[1].split('.')[0] +'_hi_rewritten.tsv', 'wb')

for line in file.readlines():
    line = line.strip().split('\t')[1]
    if line != "":
            translated = translate.translate_text(line, src_lang='en', dst_lang='hi', project_id=config["ProjectID"])
            outfile.write(translated.encode() + '\n'.encode())
outfile.close()
file.close()