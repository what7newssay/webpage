import io
import nltk
from nltk.tokenize import WhitespaceTokenizer
import json
from pprint import pprint
import string

#apply syntactic filters based on POS tags         #, 'VBD','VBG','VBN'
def filter_for_tags(tagged, tags=['NN', 'NNP', 'NNS', 'VB']):
    return [item for item in tagged if item[1] in tags]


def stem(text):
    "stemming---temp"
    
def allnoun(i,tagged,n, tags=['NN', 'NNP', 'NNS']):  # for finding ngram, sequential nouns
    if n==2:
        if tagged[i][1]in tags and tagged[i+1][1] in tags:
            return True
        else :
            return False
    if n==3:
        if tagged[i][1]in tags and tagged[i+1][1] in tags and tagged[i+2][1] in tags:
            return True
        else :
            return False
    
       
def bigrams(wordTokens,tagged):
  output = {}
  a = list(nltk.bigrams(wordTokens))
  for i in range(len(tagged)-1):
    g = ' '.join(a[i])
    if allnoun(i,tagged,2)==True:
        output.setdefault(g, 0)
        output[g] += 1
  return [item for item in output if output[item]>2]    #more than 1 = bigrams 
  
def trigrams(wordTokens,tagged):
  output = {}
  a = list(nltk.trigrams(wordTokens))
  for i in range(len(tagged)-2):
    g = ' '.join(a[i])
    if allnoun(i,tagged,3)==True:
        output.setdefault(g, 0)
        output[g] += 1
  return [item for item in output if output[item]>1]    #more than 0 = trigrams 
  

def levenshteinDistance(str1, str2):  #not be used this time
    m = len(str1)
    n = len(str2)
    lensum = float(m + n)
    d = []           
    for i in range(m+1):
        d.append([i])        
    del d[0][0]    
    for j in range(n+1):
        d[0].append(j)       
    for j in range(1,n+1):
        for i in range(1,m+1):
            if str1[i-1] == str2[j-1]:
                d[i].insert(j,d[i-1][j-1])           
            else:
                minimum = min(d[i-1][j]+1, d[i][j-1]+1, d[i-1][j-1]+2)         
                d[i].insert(j, minimum)
    ldist = d[-1][-1]
    ratio = (lensum - ldist)/lensum
    return {'distance':ldist, 'ratio':ratio}
"""eg of levenshteinDistance()
print(levenshteinDistance("kitten","sitting"))   
print(levenshteinDistance("rosettacode","raisethysword"))
"""

def freq(removedTextList,tagged):    
    output = {}
    for i in range(len(removedTextList)):
        if removedTextList[i] in tagged:
            output.setdefault(removedTextList[i], 0)
            output[removedTextList[i]] += position(i,len(removedTextList))
    return output

def position(i, size):
    #"i = sequence. of word"
    """Different sentence positions indicate different
    probability of being an important sentence.
    """
    normalized = i * 1.0 / size
    if (normalized > 1.0):
        return 0
    elif (normalized > 0.9):
        return 0.15
    elif (normalized > 0.8):
        return 0.04
    elif (normalized > 0.7):
        return 0.04
    elif (normalized > 0.6):
        return 0.06
    elif (normalized > 0.5):
        return 0.04
    elif (normalized > 0.4):
        return 0.05
    elif (normalized > 0.3):
        return 0.08
    elif (normalized > 0.2):
        return 0.14
    elif (normalized > 0.1):
        return 0.23
    elif (normalized > 0):
        return 0.17
    else:
        return 0

def extractKeyphrases(text):
    #tokenize the text using nltk
    #wordTokens = WhitespaceTokenizer().tokenize(text)   #1split(' ') can do the same thing
    punctuations = list(string.punctuation)
    punctuations.append("''")
    punctuations.append("``")
    
    temp = nltk.word_tokenize(text)
    wordTokens=[i for i in temp if i not in punctuations] #no punc. at all'
    #print("00000")
    #print(wordTokens)
    #assign POS tags to the words in the text
    tagged = nltk.pos_tag(wordTokens)
    #print("111111")
    #print(tagged)

    #n-grams keywords
    ngrams = bigrams(wordTokens,tagged)
    ngrams.extend(trigrams(wordTokens,tagged))
    
    #filter for tags
    tagged = filter_for_tags(tagged) 
    taggedtextlist = [x[0] for x in tagged]
    
    freqList=freq(wordTokens,taggedtextlist)
    sortedList=sorted(freqList, key=lambda i: int(freqList[i]))
    aThird=len(freqList)/3
    freqKey=sortedList[:aThird]
    
    keywords= freqKey
    keywords.extend(ngrams)
    
    return keywords

def toString3(list):
    return ["["+ item +"]" for item in list]
    
if __name__ == '__main__':
    inputfile = raw_input("Enter your input(json): ");
    with open(inputfile) as data_file:    
        data = json.load(data_file)
    for key in data:    
        title=data[key]["title"]
        text=data[key]["text"]
    print ",".join(toString3(extractKeyphrases(text)))












