# Finetuning BERT for translation

The code here is a slightly modified version of the code in [this repo](https://github.com/livingmagic/nmt-with-bert-tf2).
Relevant documentation and tests can be found in there.

## Dataset
Download the dataset (in this case, hindiencorp):
```
!curl --remote-name-all https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11858/00-097C-0000-0023-625F-0{/README.txt,/hindencorp05.export.gz,/hindencorp05.plaintext.gz}
! gunzip hindencorp05.plaintext.gz
```
## mBERT 
Download and unzip mBERT

```
wget https://storage.googleapis.com/bert_models/2018_11_23/multi_cased_L-12_H-768_A-12.zip
unzip multi_cased_L-12_H-768_A-12
```

## Usage

### Training
```
python3 bert_nmt.py train <dataset_file> <bert_dir> <checkpoint_dir>
```

### Testing
```
python3 bert_nmt.py test <input_file> <output_file> <bert_dir> <checkpoint>
```
