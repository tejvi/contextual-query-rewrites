# Generation of a dataset from wikipedia revision history

The method outlined in the paper [Learning to Split and Rephrase From Wikipedia Edit History](https://arxiv.org/abs/1808.09468) was followed.

## Execution:

Download and unzip the title dump file from [https://dumps.wikimedia.org/other/pagetitles/20200503/](https://dumps.wikimedia.org/other/pagetitles/20200503/)

Run Scraper.py with the path to the title dump file, followed by Dataset.py
``` 
python3 Scraper.py <path_to_dump>
python3 Dataset.py
```

the dataset will be written to ```output.tsv```

