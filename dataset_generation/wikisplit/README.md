# Generation of a dataset from wikipedia revision history

The method outlined in the paper [Learning to Split and Rephrase From Wikipedia Edit History](https://arxiv.org/abs/1808.09468) was followed.

## Execution:
Note: the HTML tags used might differ between languages, so make the necessary changes in ```scrape_wiki.py```, based on your observations.
To get the data for a different language:

1. Download and unzip the title dump file from [https://dumps.wikimedia.org/other/pagetitles/20200503/](https://dumps.wikimedia.org/other/pagetitles/20200503/).
For example, for hindi, this could be something like - ```hiwiki-20200503-all-titles-in-ns-0```

2. Identify the url. For example, for hindi, this would be - ```"https://hi.wikipedia.org/w/api.php```

3. Run ```scrape_wiki.py``` with the path to the title dump file and the url. The data will get written to ```raw_data```.
``` 
python3 scrape_wiki.py <path_to_title_dump> <url>
```
4. Run ```transform_data.py```. The output will get written to ```output.tsv```
```
python3 transform_data.py
```

