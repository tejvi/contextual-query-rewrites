# hi-LT with hindi queries
Hindi queries are run on Lasertagger trained on a translated corpus. 

en-Wikisplit is translated to hindi to train this model.


To translate the dataset:
```
python3 translate_wikisplit.py <path_to_wikisplit_dir>
```

The translated files will be written to ```wikisplit_translated```

Lasertagger is trained on BERT base, cased model.
However, for this, mBERT model is needed.
```
wget https://storage.googleapis.com/bert_models/2018_11_23/multi_cased_L-12_H-768_A-12.zip
```

The remainder of the steps are the same as those for en-LaserTagger.
However, change vocab size in config file of lasertagger to 119547.
```
 echo '{  "attention_probs_dropout_prob": 0.1,  "hidden_act": "gelu",  "hidden_dropout_prob": 0.1,  "hidden_size": 768,  "initializer_range": 0.02,  "intermediate_size": 3072,  "max_position_embeddings": 512,  "num_attention_heads": 12,  "num_hidden_layers": 12,  "type_vocab_size": 2,  "vocab_size":119547,  "use_t2t_decoder": false,  "decoder_num_hidden_layers": 1,  "decoder_hidden_size": 768,  "decoder_num_attention_heads": 4,  "decoder_filter_size": 3072,  "use_full_attention": false}' > mbert_conf.json
 ```
use mbert_conf as the config file while using lasertagger.
