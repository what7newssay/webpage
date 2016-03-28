__author__ = 'Chun-kit YEUNG'

import newspaper
from newspaper import Article
from langdetect import detect
from langdetect import lang_detect_exception
import articleProcessor as ap

NEWS_SOURCES_URLS = [
    'http://edition.cnn.com',
    'http://www.washingtonpost.com',
    'http://www.bbc.com',
    'http://www.nytimes.com/',
]

def build_news_source(news_sources_urls = NEWS_SOURCES_URLS):
    print ("building news sources")
    news_sources = [newspaper.build(paper) for paper in news_sources_urls]
    
    return news_sources


def build_articles(news_sources):
    print("Start downloading articles")
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
                    ap.process_and_save_article(article = article, news_brand = paper.brand)
                    print ("{0}-{1}".format(i,size), "Yes-en:", article.url)
            except (newspaper.article.ArticleException, lang_detect_exception.LangDetectException):
                print ("{0}-{1}".format(i,size), "Non-en:", article.url) 

def start():
    news_sources = build_news_source()
    build_articles(news_sources)

if __name__ == '__main__':
    #test()
    start()
    print ("end of function")
