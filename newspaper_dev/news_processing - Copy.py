__author__ = 'YEUNG Chun Kit'

from newspaper import Article
import newspaper
import json
import codecs
import os
import time
import datetime
import re
from langdetect import detect
from langdetect import lang_detect_exception
import geoExtractor 
#from bson import json_util

list_of_useless_regex = [
    'Advertisement Continue reading the main story',
    'Image copyright.*Image caption'
    'Image copyright',
    'Image caption',
    'Hide Caption [0-9]+ of [0-9]+',
    '[0-9]+ photos:',
    'Media caption'
    ]

def clean_text(text):
    for regex in list_of_useless_regex:
        text = re.sub(regex, '', text)

    return text

def get_serialized_article_obj(article):
    s_a = {}
    s_a['url'] = article.url
    s_a['title'] = article.title
    s_a['top_image'] = article.top_image
    s_a['meta_img'] = article.meta_img
    s_a['images'] = article.images
    s_a['movies'] = article.movies
    s_a['text'] = article.text
    s_a['tags'] = article.tags
    s_a['keywords'] = article.keywords 
    s_a['meta_keywords'] = article.meta_keywords
    s_a['authors'] = article.authors
    s_a['publish_date'] = article.publish_date
    s_a['summary'] = article.summary 
    s_a['source_url'] = article.source_url

    return s_a



def get_article_filename(title):
    #replace any non-alphanumeric to '-'
    filename = re.sub('[^0-9a-zA-Z]+', '-', title)

    # the filename should be shorter than 255,
    # to play safe, set it to first 240 chara
    if len(filename) > 250:
        filename = filename[:240]
    filename += '.json'
    return filename


def get_path_to_save(article):
    t = article.publish_date
    filename = get_article_filename(article.title)
    #the base path
    path_to_save = './data'
    
    path_to_save = os.path.join(path_to_save, str(t.year))
    path_to_save = os.path.join(path_to_save, str(t.month))
    path_to_save = os.path.join(path_to_save, str(t.day))
    path_to_save = os.path.join(path_to_save, filename)

    return path_to_save
        

def create_file(path_to_save, data = None):
    #transform the dir_path to absolute path
    abs_save_path = os.path.abspath(path_to_save)
    abs_dir_path = os.path.dirname(abs_save_path)

    
    #create a directory if it doesn't exist
    if not os.path.exists(abs_dir_path):
        os.makedirs(abs_dir_path)

    #save the data
    print (abs_save_path)
    with codecs.open(abs_save_path, 'w', 'utf-8') as f:
        f.write(json.dumps(data, indent=4, default=to_json))

def get_news_location(article, num_of_location=3):
    extractor = geoExtractor.Extractor(text = article.text)
    extractor.find_entities()
    ranks = extractor.get_entities_with_count().most_common(num_of_location)
    locations = []
    for rank in ranks:
        locations.append(rank[0])
    return locations

def build_news_source():
    print ("building news sources")
    paper_urls = []
    paper_urls.append('http://edition.cnn.com')
    paper_urls.append('http://www.washingtonpost.com')
    paper_urls.append('http://www.bbc.com')
    paper_urls.append('http://www.nytimes.com/')

    papers = [newspaper.build(paper_url) for paper_url in paper_urls]
    
    return papers

def process_and_save_article(article, news_brand=""):
    if article.publish_date is None:
        #today date
        today = time.time()
        today = datetime.datetime.fromtimestamp(today)
        article.publish_date = today

    article.text = clean_text(text = article.text)
    article.summary = clean_text(text = article.summary)
    path_to_save = get_path_to_save(article)
    data_a = get_serialized_article_obj(article)
    data_a['news_brand'] = news_brand
    data_a['location'] = get_news_location(article, num_of_location=3)
    create_file(path_to_save, data = data_a)

def build_articles(news_sources):
    print("Start downloading articles")
    articles = []
    i = len(news_sources)
    for paper in news_sources:
        i -= 1
        size = paper.size()
        for article in paper.articles:
            size -= 1
            try:
                article.build()
                article_lang = detect(article.text)
                if article_lang == 'en':
                    #articles.append(article)
                    process_and_save_article(article = article, news_brand = paper.brand)
                    print ("{0}-{1}".format(i,size), "Yes-en:", article.url)
            except (newspaper.article.ArticleException, lang_detect_exception.LangDetectException):
                print ("{0}-{1}".format(i,size), "Non-en:", article.url)

    return articles
    

def generate_article_key(article):
    pass
    #TODO: think of how the primary key is generated with the aricle

   
def to_json(obj):
    if isinstance(obj, datetime.datetime):
        return {'__class__': 'datetime',
                '__value__': obj.isoformat()}
    elif isinstance(obj, set):
        return list(obj)
    
    raise TypeError(repr(obj) + ' is not JSON serializable')



def test_save_article_function():
    from newspaper import Article
    today = time.time()
    today = datetime.datetime.fromtimestamp(today)
    url = 'http://www.bbc.com/news/world-europe-35828810'
    #url = 'http://fox13now.com/2013/12/30/new-year-new-laws-obamacare-pot-guns-and-drones/'
    a = Article(url)
    a.build()
    #print (a.title, a.publish_date)

    #if the news has no publish_date, set it to today
    if a.publish_date is None:
        a.publish_date = today

    path_to_save = get_path_to_save(a)
    data_a = get_serialized_article_obj(a)
    create_file(path_to_save, data = data_a)

def test():
    #url = 'http://money.cnn.com/2016/02/26/investing/warren-buffett-berkshire-hathaway-annual-shareholder-letter/index.html?section=money_topstories'
    #url = 'http://www.bbc.com/hindi/sport/2016/02/160227_heart_change_for_kohli_fan_dil'
    #url = 'http://www.bbc.com/news/world-europe-35828810'
    #url = 'http://fox13now.com/2013/12/30/new-year-new-laws-obamacare-pot-guns-and-drones/'
    url = 'http://www.nytimes.com/2016/03/19/world/europe/dubai-airliner-crashes-while-trying-to-land-at-russian-airport.html?hp&action=click&pgtype=Homepage&clickSource=story-heading&module=first-column-region&region=top-news&WT.nav=top-news&_r=1'
    print ("building:", url)
    a = Article(url)
    a.build()
    process_and_save_article(a)

    print ("first paragraph")
    print (a.text.split('\n')[0])
    print ("Summary:")
    print (a.summary)   
    
    try:
        print (detect(a.text))
    except lang_detect_exception.LangDetectException:
        print ("Not English")
        

def main():
    news_sources = build_news_source()
    news_articles = build_articles(news_sources)

if __name__ == '__main__':
    test()
    #main()
    print ("end of function")
