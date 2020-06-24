# en-LT with translated queries
Hindi queries are run on Lasertagger trained on an English corpus. 

Hindi queries are translated to English before being input to the LaserTagger and the outputs are translated back to hindi.

To use the model:

input_file: contains hindi queries in the format ```hindi_query1 <::::> hindi_query2```

Run the following to convert it into the right format for lasertagger

``` 
python3 preprocess.py <input_file.txt>
```

this creates a file ```input_file_translated.tsv``` which can be input to the lasertagger.

inference:

```
python3.7 lasertagger/predict_main.py   --input_file=<input_file_translated.tsv> --input_format=wikifuse   --output_file=<output_file.tsv>   --label_map_file=<path_to_label_map.txt   >--vocab_file=<path_to_bert_vocab.txt>   --saved_model=<path_to_exported_model>
```

Finally, run the following for the rewritten hindi queries
```
python3 postprocess <output_file.tsv>
```

the final hindi queries can be found at output_file_hi_rewritten.tsv