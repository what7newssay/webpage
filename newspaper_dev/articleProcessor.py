__author__ = 'YEUNG Chun Kit'

from newspaper import Article
import json
import codecs
import os
import time
import datetime
import re
import geoExtractor as geoEx
import summaryExtractor as sumEx
import uuid
#from bson import json_util

LIST_OF_USELESS_TEXT_REGEX = [
    'Advertisement Continue reading the main story',
    'Image copyright.*Image caption',
    'Image copyright',
    'Image caption',
    'Hide Caption [0-9]+ of [0-9]+',
    '[0-9]+ photos:',
    'Media caption',
    'flickr.com',
    ]
    
LIST_OF_IMG_USELESS_REGEX = [
    'static\.bbci\.co\.uk.*',
    'edition\.i\.cdn\.cnn\.com.*',
    'ewn\.co\.za/site/design.*',
]

CLEAN_TARGET_LIST = {
    'text': LIST_OF_USELESS_TEXT_REGEX,
    'image': LIST_OF_IMG_USELESS_REGEX,
}


SUMMARY_METHODS_LIST = [ 
    'luhn',
    'edmundson',
    'lsa',
    'text_rank',
    'lex_rank',
    'sum_basic',
    'kl',
]

def clean_text(text, target = 'text'):
    useless_list = CLEAN_TARGET_LIST[target]
    for regex in useless_list:
        text = re.sub(regex, '', text)
    return text
    
def clean_img():
    pass

def process_and_save_article(article, news_brand=""):
    #set publish_date in case of None
    if article.publish_date is None:
        #today date
        today = time.time()
        today = datetime.datetime.fromtimestamp(today)
        article.publish_date = today

    #clean article text
    article.text = clean_text(text = article.text, target = 'text')
    article.summary = clean_text(text = article.summary)

    #save the file
    path_to_save = get_path_to_save(article)
    data_a = get_serialized_article_obj(article)
    data_a['news_brand'] = news_brand
    create_file(path_to_save, data = data_a)

def list_to_string(str_list = []):
    result_str = ''
    
    for sentence in str_list:
        result_str += sentence
        result_str += ';;;'

    return result_str


def get_serialized_article_obj(article):
    s_a = {}
    
    #serialized the attributes from the article class itself
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
    s_a['source_url'] = article.source_url

    #the original summary from text_teaser
    s_a['text_teaser_summary'] = list_to_string(str_list = [sentence for sentence in article.summary.split('\n')])
    
    #get geoLocation
    s_a['geoLocation'] = geoEx.get_locations(
            input_str = article.text, 
            num_of_locations = 3)

    #generate uuid 
    s_a['unique_id'] = uuid.uuid4().hex

    #get other summaries
    for method in SUMMARY_METHODS_LIST:
        temp_summary = sumEx.get_summary(
            summarize_method = method,
            input_str = article.text,
            language = 'english',
            num_of_sentences = 5)

        s_a[method+'_summary'] = list_to_string(str_list = [sentence._text for sentence in temp_summary])

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
    path_to_save = '/home/zhengzhenggao/ServerWeb/articles/original'
    
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


    
def generate_article_key(article):
    pass
    #TODO: think of how the primary key is generated with the aricle

   
def to_json(obj):
    if isinstance(obj, datetime.datetime):
        return {'__class__': 'datetime',
                '__value__': obj.strftime("%Y-%m-%d")}
    elif isinstance(obj, set):
        return list(obj)
    
    raise TypeError(repr(obj) + ' is not JSON serializable')

def test():
    url = 'http://www.bbc.com/news/world-europe-35828810'
    a = Article(url)
    a.build()
    process_and_save_article(a, 'bbc')

if __name__ == '__main__':
    test()
