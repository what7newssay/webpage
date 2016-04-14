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
         
    score={}
    for item1 in longestList:
        for item2 in item1:
            if type(item2) is list:
                score[" ".join(item2)] = checkScore(" ".join(item2) ,all_content_keywords)
            if type(item2) is str:
                score[item2] = checkScore(item2 ,all_content_keywords)
    
    sortedScoreList= sorted(score.items(), key=operator.itemgetter(1))
    if len(sortedScoreList)>0 :
        longestNgram = sortedScoreList[-1][0]
    else:
        longestNgram = "no title"
    
    freq={}
    common_uni =""
    if len(list_uni)>0 :
        for i in list_uni:
            for j in i:
                freq.setdefault(j, 0)       
                freq[j]  += 1
        freqList2 =sorted(freq.items(), key=operator.itemgetter(1))
        freqList2.reverse()
        if len(freqList2)>0:
            for i in freqList2:
                if (i[0] not in longestNgram) and (i[1] >= len(title)/2):
                    common_uni= common_uni + " # " +i[0]
                    break 
    
    name = "# "+longestNgram + common_uni
            
    return name
            
    #print("longestNgram & its score:")
    #print((longestNgram))
    #print(sortedScoreList[-1][1])
            
            
            
 
if __name__ == '__main__':     
   
    title=[]
    title.append(['FlyDubai Plane Crashes', 'Russian Airport', 'Killing'])
    title.append(['Russia plane crash', 'Rostov-on-Don'])
    title.append(['Flydubai plane crashes','Russia'])
    title.append(['Dubai passenger jet' ,'passenger jet crashes', 'Russia',])
    all_content_keywords=['Russian', 'crash', 'plane', 'website', 'passengers', 'statement', 'Golubev', 'landing', 'airport', 'FlyDubai', 'Dubai', 'Interfax', 'officials', 'attempt', 'Rostov', 'agency', 'Photo', 'Mr.', 'Rostov-on-Don', 'Saturday', 'members', 'government', 'crew', 'airline', 'Boeing', 'governor', 'Investigative', 'Committee', 'city', 'victims', '\u201d', 'runway', 'people', 'air', 'Russia\u2019s', 'year', 'airline\u2019s', 'region', 'MOSCOW', 'list', 'winds', '\u201cWe', 'budget', 'none', 'airliner', 'carrier', 'Uzbek', 'everything', 'factors', 'help', 'factors\u201d', 'data', 'law', 'al-Ghaith', 'Ghaith', 'error', 'plane', 'FlyDubai', 'crash', 'passengers', 'crew', 'A', 'runway', 'land', 'aircraft', 'Boeing', 'Dubai', 'attempt', 'carrier', 'cost', 'BBC', 'passenger', 'officials', 'jet', 'city', 'Rostov-on-Don', 'board', 'Saturday', 'time', 'visibility', 'victims', 'GMT', 'factor', 'children', 'winds', 'al-Ghaith', 'Ukrainians', 'co-pilot', 'Cypriot', 'pilot', 'head', 'Spaniard', 'airline', 'Ghaith', 'airport', 'victims', 'plane', 'Dubai', 'passengers', 'news', 'Aviation', 'Ghaith', 'UAE', 'Rostov-on-Don', 'crash', 'hours', 'families', 'state', 'flydubai', 'a.m.', 'weather', 'Boeing', 'Vladimir', 'media', 'CNN', 'Sunday', 'pilot', 'statement', 'Emirates', 'Arab', 'United', 'Al', 'flight', 'recorders', 'aircraft', 'winds', 'landing', 'land', 'Puchkov', 'Kovrizhnaya', 'runway', 'minister', 'Sputnik', 'CEO', 'government', 'Saturday', 'search', 'members', 'U.S.', 'operation', 'cause', 'investigators', 'moment', 'Federal', 'passenger', 'Video', 'crew', 'Administration', 'people', 'take', 'impact', 'show', 'reporters', 'children', 'airline', 'visibility', 'end', 'effort', '@', 'accident', 'March', '\u2014', 'condolences', 'deepest', 'know', 'Emergency', 'Maktoum', 'attempt', 'terrorism', 'Authorities', 'Minister', 'jet', 'ET', 'feet', 'point', 'come', 'mph', 'Friday', 'clear', 'law', 'investigations', 'Oksana', 'error', 'Russian', 'Dubai', 'jet', 'officials', 'FlyDubai', 'aboard', 'Rostov-on-Don', 'passenger', 'crash', 'people', 'Russia', 'plane', 'attempt', 'land', 'city', 'Reuters', 'Russia\u2019s', 'landing', '\u201d', 'passengers', 'crew', 'flight', 'Saturday', 'members', 'board', 'Rostov', 'statement', 'airport', 'Boeing', 'Photos', 'second', 'airliner', 'recorder', 'winds', 'al-Ghaith', 'Investigative', 'Committee', 'news', 'Interfax', 'government', 'Vladimir', 'one', 'site', 'budget', 'carrier', 'aviation', 'region', 'A', 'runway', 'Ministry', 'weather', '\u201cpoor', 'flames', 'conditions', 'approach', 'plane\u2019s', 'break', 'read']
   
    print(name(title, all_content_keywords))
    

       

