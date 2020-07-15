# Finetuning BERT for translation

The code here is a slightly modified version of the code in [this repo](https://github.com/livingmagic/nmt-with-bert-tf2).
Relevant documentation and tests can be found in there.

## Dataset
Download the dataset (in this case, hindiencorp):
```
curl --remote-name-all https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11858/00-097C-0000-0023-625F-0{/README.txt,/hindencorp05.export.gz,/hindencorp05.plaintext.gz}
gunzip hindencorp05.plaintext.gz
```
## mBERT 
Download and unzip mBERT

```
wget https://storage.googleapis.com/bert_models/2018_11_23/multi_cased_L-12_H-768_A-12.zip
unzip multi_cased_L-12_H-768_A-12
```

## Usage

target language : "en" for conversion from a (indic) language to english.
Any other word would mean conversion from english.

### Training
```
python3 bert_nmt.py train <target_lang> <dataset_file> <bert_dir> <checkpoint_dir>
```
When the training loop runs for the specified number of epochs, checkpoint file ```bert_nmt_ckpt_<targ_lang>.index``` will be created. Use this as the checkpoint file for testing.
### Testing
```
python3 bert_nmt.py test <target_lang> <input_file> <output_file> <bert_dir> <checkpoint>
```
