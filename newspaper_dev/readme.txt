newspaper_dev README, __author__ = 'Chun-kit YEUNG'
======================================
A new program, geoExtractor, have been created to extract location information of a news.

This program will depend on the files from NLTK and please download these file.
You may download those files via python with the following commands:
$ python3
>>>import nltk

>>>nltk.downloader.download('maxent_ne_chunker')
>>>nltk.downloader.download('words')
>>>nltk.downloader.download('treebank')
>>>nltk.downloader.download('maxent_treebank_pos_tagger')
>>>nltk.downloader.download('punkt')
>>>nltk.downloader.download('averaged_perceptron_tagger')

It should work fine now. Please let me know should there be any problems.
======================================
- This program fetched only English news from BBC, CNN, WSTP and NYT. Then, parse and perform some NLP operations on the news. 

- During Parsing, the author(s) of the article(authors), the date publishing the article(publish_date), the original text(text), title of the news(title), images in the news(top_image/images), vedio exist in the url(movies), news source(news_brand/source_url), the tags exist in the html meta element(tags), and the keywords extracted from html meta element(meta_keywords) are parsed.

- During NLP, keywords and summary of the news are extracted based on text teaser's algorithm, selecting the top five sentences according to the position of the sentence, length of the sentence, number of keywords exist in the sentence and number of title-words exist in the sentence.
======================================
1. Run this program

    This program is run under python3 and dependent on python libraries, newspaper and langdetect. The following will descript how to install the dependencies and how to run the program under Ubuntu.

i. Install newspaper
    - Install pip3 command needed to install newspaper3k package:
        $ sudo apt-get install python3-pip
    - Python development version, needed for Python.h:
        $ sudo apt-get install python-dev
    - lxml requirements:
        $ sudo apt-get install libxml2-dev libxslt-dev
    - For PIL to recognize .jpg images:
        $ sudo apt-get install libjpeg-dev zlib1g-dev libpng12-dev
    - Install the distribution via pip:
        $ pip3 install newspaper3k
    - Download NLP related corpora:
        $ curl https://raw.githubusercontent.com/codelucas/newspaper/master/download_corpora.py | python3

ii. Install langdetect
    - Install the langdetect via pip:
        $ pip3 install langdetect
    
iii. Run the program
    - Change your working directory to where you save news_processing.py
        $ cd /Path/to/save/directory
    - Run the program
        $ python3 news_processing.py

iv. Result
    During runing the program, you will see what news is being building. When finished, you will see each news is extracted and stored in './data/YEAR/MONTH/DAY' according to its publish_date. And the following attributes are saved in the json format.

======================================
This program will download the article from BBC, CNN, WSTP and NYT.

The following attributes are saved as .json format.
    url:          the url of the article [key]
    news_brand:    the name of news brand
    source_url:   the news brand's url
    title:        the title of the article
    top_image:    the biggest image in the article
    images:       all images exist in the url
    movies:       all vedio exist in the url
    text:         the content(corpus) of the article
    tags:         the tags exist in the html meta element
    keywords:     the top (10) keywords of the article
    meta_keywords: the keywords extracted from html meta element
    authors:      the author(s) of the article
    publish_date: the date publishing the article
    summary:      the text summary of the corpus


======================================
Note:
1. [FIXED]BBC is consisted of multiple languages and hence the news article inside the json file is not only in English, but also from Chinese to Russian.
2. Some of the attributes above is duplicated and not preferable as a database schema name. The json file and the python program will be refined later soon.
  i. "new source" is not preferable
  ii."new source"'s and "source_url"'s meaning are somewhat duplicated
3. "tags", "meta_keywords" and "movies" cannot be extracted yet
4. "source_url" is currently exist in the NYT_article.json ONLY


