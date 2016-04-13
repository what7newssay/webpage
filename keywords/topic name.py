import io
import nltk
from nltk.tokenize import WhitespaceTokenizer
import json
from pprint import pprint
import string
import operator
import codecs

"""
1)我知道佢地係一group 再抽common title-keywords得唔得？
2) longest ngram+common unigram
"""

def String2List(keywordList):
# a trigram keyword is converted to a list of 3 string(unicode)
#like this: [[u'FlyDubai', u'Plane', u'Crashes'], [u'Russian', u'Airport'], [u'Killing']]
    temp = []
    for i in keywordList:
        temp.append(list(i.split()))       
    return temp   

def make_4_and_5_gram_list(list_bi,list_tri):
    list_4 = []
    list_5 = []
    temp=[]
    if len(list_tri)> 0 :
        for index,item in enumerate(list_tri):
            if len(list_tri)>1 :            
                rest_of_list = list_tri[index+1:]
                for i in range(len(rest_of_list)):
                    if item[0] == rest_of_list[i][-1]:
                        temp = rest_of_list[i][:]
                        temp.extend(item[1:])
                        list_5.append(temp)
                        
                    elif item[-1] == rest_of_list[i][0]:                      
                        temp = item[:]
                        temp.extend(rest_of_list[i][1:])
                        list_5.append(temp)
                        
                    elif (item[0]==rest_of_list[i][1]) and (item[1]==rest_of_list[i][2]):
                        temp = rest_of_list[i][:]
                        temp.extend(item[2:])
                        list_4.append(temp)
                        
                    elif (item[1]==rest_of_list[i][0]) and (item[2]==rest_of_list[i][1]):
                        temp = item[:]
                        temp.extend(rest_of_list[i][2:])
                        list_4.append(temp)
                        
            if len(list_bi)> 0 :
                for j in range(len(list_bi)):
                    if item[0]==list_bi[j][1]: 
                        temp = list_bi[j][:]
                        temp.extend(item[1:])
                        list_4.append(temp)
                        
                    elif item[2]==list_bi[j][0]: 
                        temp = item[:]
                        temp.extend(list_bi[j][1:])
                        list_4.append(temp)

    return list_4,list_5
    
def findLongest(list_uni,list_bi,list_tri,list_4,list_5):
    if len(list_5)!=0:
        return list_5
    elif len(list_4)!=0:
        return list_4
    elif len(list_tri)!=0:
        return list_tri
    elif len(list_bi)!=0:
        return list_bi
    elif len(list_uni)!=0:
        return list_uni
    else:
        return []
        
def string2SingleString(list2): # remove duplicate already
    temp = []
    for i in list2:
        temp.extend(i.split())
    return temp

def checkScore(List,all_content_keywords):
    score =0
    for item in all_content_keywords:
        if item in List:
            score +=1
    return score
            
    
    
def name(title,all_content_keywords):
    # singleList[i]= single list of title[i]
    #singleList[i]=[[u'FlyDubai', u'Plane', u'Crashes'], [u'Russian', u'Airport'], [u'Killing']]
    singleList = []
    for i in range(len(title)):  
        singleList.append(String2List(title[i]))
        
    list_uni =[]
    list_bi  =[] #list_bi[i]=single list of bi gram of title[i]
    list_tri =[] #list_tri[i]=single list of tri gram of title[i]
    list_4   =[] #list_4[i]=single list of 4-gram of title[i]
    list_5   =[] #list_5[i]=single list of 5-gram of title[i]
    longestList=[]
    
    for i in range(len(title)):
        list_uni.append(string2SingleString(title[i]))
        list_bi.append([item for item in singleList[i] if len(item) == 2 ])
        list_tri.append([item for item in singleList[i] if len(item) == 3 ])
        four,five = make_4_and_5_gram_list(list_bi[i], list_tri[i])
        list_4.append(four)
        list_5.append(five)
        longestList.append(findLongest(list_uni[i],list_bi[i],list_tri[i],list_4[i],list_5[i]))
        print(i)
        print(list_uni[i])
        print(list_bi[i])
        print(list_tri[i])
        print(list_4[i])
        print(list_5[i])
        print(longestList[i])
        
    score={}
    for item1 in longestList:
        for item2 in item1:
            score[" ".join(item2)] = checkScore(" ".join(item2) ,all_content_keywords)
    
    sortedScoreList= sorted(score.items(), key=operator.itemgetter(1))
    longestNgram = sortedScoreList[-1][0]
    print("longestNgram & its score:")
    print(type(longestNgram))
    
    print(sortedScoreList[-1][1])
    return longestNgram
 
if __name__ == '__main__':     
   
    title=[]
    title.append([u'FlyDubai Plane Crashes', u'Russian Airport', u'Killing', u'Crashes orange', u'Airport love you'])
    title.append([u'Russia plane crash', u'Rostov-on-Don'])
    title.append([u'Flydubai plane crashes', u'Russia'])
    title.append([  u'Dubai passenger jet' u'passenger jet crashes', u'Russia',])
    all_content_keywords=[u'Russian', u'crash', u'plane', u'website', u'passengers', u'statement', u'Golubev', u'landing', u'airport', u'FlyDubai', u'Dubai', u'Interfax', u'officials', u'attempt', u'Rostov', u'agency', u'Photo', u'Mr.', u'Rostov-on-Don', u'Saturday', u'members', u'government', u'crew', u'airline', u'Boeing', u'governor', u'Investigative', u'Committee', u'city', u'victims', u'\u201d', u'runway', u'people', u'air', u'Russia\u2019s', u'year', u'airline\u2019s', u'region', u'MOSCOW', u'list', u'winds', u'\u201cWe', u'budget', u'none', u'airliner', u'carrier', u'Uzbek', u'everything', u'factors', u'help', u'factors\u201d', u'data', u'law', u'al-Ghaith', u'Ghaith', u'error', u'plane', u'FlyDubai', u'crash', u'passengers', u'crew', u'A', u'runway', u'land', u'aircraft', u'Boeing', u'Dubai', u'attempt', u'carrier', u'cost', u'BBC', u'passenger', u'officials', u'jet', u'city', u'Rostov-on-Don', u'board', u'Saturday', u'time', u'visibility', u'victims', u'GMT', u'factor', u'children', u'winds', u'al-Ghaith', u'Ukrainians', u'co-pilot', u'Cypriot', u'pilot', u'head', u'Spaniard', u'airline', u'Ghaith', u'airport', u'victims', u'plane', u'Dubai', u'passengers', u'news', u'Aviation', u'Ghaith', u'UAE', u'Rostov-on-Don', u'crash', u'hours', u'families', u'state', u'flydubai', u'a.m.', u'weather', u'Boeing', u'Vladimir', u'media', u'CNN', u'Sunday', u'pilot', u'statement', u'Emirates', u'Arab', u'United', u'Al', u'flight', u'recorders', u'aircraft', u'winds', u'landing', u'land', u'Puchkov', u'Kovrizhnaya', u'runway', u'minister', u'Sputnik', u'CEO', u'government', u'Saturday', u'search', u'members', u'U.S.', u'operation', u'cause', u'investigators', u'moment', u'Federal', u'passenger', u'Video', u'crew', u'Administration', u'people', u'take', u'impact', u'show', u'reporters', u'children', u'airline', u'visibility', u'end', u'effort', u'@', u'accident', u'March', u'\u2014', u'condolences', u'deepest', u'know', u'Emergency', u'Maktoum', u'attempt', u'terrorism', u'Authorities', u'Minister', u'jet', u'ET', u'feet', u'point', u'come', u'mph', u'Friday', u'clear', u'law', u'investigations', u'Oksana', u'error', u'Russian', u'Dubai', u'jet', u'officials', u'FlyDubai', u'aboard', u'Rostov-on-Don', u'passenger', u'crash', u'people', u'Russia', u'plane', u'attempt', u'land', u'city', u'Reuters', u'Russia\u2019s', u'landing', u'\u201d', u'passengers', u'crew', u'flight', u'Saturday', u'members', u'board', u'Rostov', u'statement', u'airport', u'Boeing', u'Photos', u'second', u'airliner', u'recorder', u'winds', u'al-Ghaith', u'Investigative', u'Committee', u'news', u'Interfax', u'government', u'Vladimir', u'one', u'site', u'budget', u'carrier', u'aviation', u'region', u'A', u'runway', u'Ministry', u'weather', u'\u201cpoor', u'flames', u'conditions', u'approach', u'plane\u2019s', u'break', u'read']
    print(name(title, all_content_keywords))
    

       

