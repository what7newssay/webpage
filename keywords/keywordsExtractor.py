import io
import nltk
from nltk.tokenize import WhitespaceTokenizer
import json
from pprint import pprint
import string
import operator
import codecs



#apply syntactic filters based on POS tags         #, 'VBD','VBG','VBN'
def filter_for_tags(tagged, tags=['NN', 'NNP', 'NNS', 'VB']):
    return [item for item in tagged if item[1] in tags]

def remove_question_word(list):
    question_word = ["Can","Could","Will","Would","Shall","May", "What","Who","Where","When","Why","Which","How"]
    return [word for word in list if word not in question_word]

def stem(text):
    "stemming---temp"
                                   #"VBN"
def allnoun(i,tagged,n, tags=['NN', 'NNP', 'NNS' ,"VBG","JJ", "VBN"]):  # for finding ngram, sequential nouns
    verb = ["VBN", "VBG"]
    if n==2:
        if (tagged[i][1]in tags and tagged[i+1][1] in tags) and (tagged[i+1][1] not in verb):
            return True
        else :
            return False
    if n==3:
        if (tagged[i][1]in tags and tagged[i+1][1] in tags and tagged[i+2][1] in tags) and (tagged[i+2][1] not in verb):
            return True
        else :
            return False
 
def ifin(m_gram,n_gram): 
#print a new bigram list such that no ducplicate elements appear in both bi- and tri-gram.
    newM = []
    for i in m_gram:
        temp = False 
        for j in n_gram:
            if i in j:
                temp = True
                break
        if temp == True:
            continue
        else: 
            newM.append(i)
    return newM
             
def trigrams(wordTokens,tagged,threshold):
  output = {}
  a = list(nltk.trigrams(wordTokens))
  for i in range(len(tagged)-2):
    g = ' '.join(a[i])
    if allnoun(i,tagged,3)==True:
        output.setdefault(g, 0)
        output[g] += 1
  return [item for item in output if output[item]>threshold]    #more than 0 = trigrams   
       
def bigrams(wordTokens,tagged,threshold):
  output = {}
  a = list(nltk.bigrams(wordTokens))
  for i in range(len(tagged)-1):
    g = ' '.join(a[i])
    if allnoun(i,tagged,2)==True:
        output.setdefault(g, 0)
        output[g] += 1
  return [item for item in output if output[item]>threshold]    #more than 1 = bigrams 



def freq(tokens,tagged):    
    output = {}
    for i in range(len(tokens)):
        if tokens[i] in tagged:
            output.setdefault(tokens[i], 0)
            #output[removedTextList[i]] += position_normal(i,len(removedTextList))
            output[tokens[i]] +=1
    return output

def position_normal(i, size):
    #"i = sequence. of word"
    """Different sentence positions indicate different
    probability of being an important sentence.
    """
    normalized = i * 1.0 / size
    if (normalized > 1.0):
        return 0
    elif (normalized > 0.9):
        return 0.1
    elif (normalized > 0.8):
        return 0.2
    elif (normalized > 0.7):
        return 0.3
    elif (normalized > 0.6):
        return 0.4
    elif (normalized > 0.5):
        return 1.0
    elif (normalized > 0.4):
        return 1.2
    elif (normalized > 0.3):
        return 1.4
    elif (normalized > 0.2):
        return 2.4
    elif (normalized > 0.1):
        return 2.7
    elif (normalized > 0):
        return 3.0
    else:
        return 0

def preprocess(text):
    punctuations = list(string.punctuation)
    punctuations.append("''")
    punctuations.append("``")
    punctuations.append(u"\xe2") 
    punctuations.append(u"\xe2") 
    punctuations.remove('-')
    
    #add space before and behind punctuation 
    new_text = ""
    for t in text:
        if t not in punctuations:
            new_text= new_text+t
        else:
            new_text= new_text+ " "+t+" " 
            
    return nltk.word_tokenize(new_text)

def ngrams(unigram, bigram, trigram):
    keywords = []
    temp13 = []
    temp12 = []
    temp23 = []
    
    temp13 = ifin(unigram,trigram)
    temp12 = ifin(temp13 ,trigram)
    temp23 = ifin(bigram ,trigram)
    
    keywords.extend(trigram) 
    keywords.extend(temp23) 
    keywords.extend(temp12) 
    return keywords           
            
def extractKeyphrases(text):
    #tokenize the text using nltk
    tokens = preprocess(text)
    
    #assign POS tags to the words in the text
    tagged = nltk.pos_tag(tokens)                       #print(tagged)
          
    #filter for tags
    filteredtagged = filter_for_tags(tagged) 
    taggedtextlist = [x[0] for x in filteredtagged]
    
    #get the frequency of each token
    freqDict   = freq(tokens,taggedtextlist)       #can show key with freq within a range
    
    #sort the freqDict and return a list, smaller no. in front
    sortedList = sorted(freqDict.items(), key=operator.itemgetter(1)) #sortedList=sorted(freqDict.items(), key=lambda t: t[0])
    # need the last one third of freqDict
    aThird     = (len(sortedList)/3)*2
    freqKey    = sortedList[aThird:]
   
    #n-grams keywords
    unigram = [each[0] for each in freqKey] 
    bigram  = bigrams(tokens, tagged, 2)
    trigram = trigrams(tokens, tagged, 1)
    keywords= ngrams(unigram, bigram, trigram)
    #for each in ngrams:
    #    print("{"+ each +":" + str(text.count(each)) +"}")
    
    return keywords
    
def extract_title(title): #title

    temp_title= nltk.word_tokenize(title)
    #remove question word for title
    new_title=remove_question_word(temp_title)
    
    #assign POS tags to the words in the title
    tagged_title = nltk.pos_tag(new_title)

    #n-grams keywords
    ngrams_title = trigrams(new_title,tagged_title,0)
    new_bi_title=ifin(bigrams(new_title,tagged_title,0),ngrams_title)
    ngrams_title.extend(new_bi_title) 
    
    nnp_tags=["NNP","JJ","CD"]
    nnp_list= [word[0] for word in tagged_title if word[1] in nnp_tags]
    new_nnp_list=ifin(nnp_list,ngrams_title)
    
    output=ngrams_title+new_nnp_list
    return output     
    
def toString3(list):
    return ["["+ item +"]" for item in list]     

def grouping(base,list1,list2,list3,list4):
    set0=set(base)
    set1=set(list1)
    set2=set(list2)
    set3=set(list3)
    set4=set(list4)
    sameGroup = []
    if len(set0.intersection(set1)) >4:
        sameGroup.extend(["set1"])
    if len(set0.intersection(set2)) >4:
        sameGroup.extend(["set2"])
    if len(set0.intersection(set3)) >4:
        sameGroup.extend(["set3"])
    if len(set0.intersection(set4)) >4:
        sameGroup.extend(["set4"])
    return sameGroup

def makeSingleString(list):
    newList = []
    for i in list:
        newList.extend(i.split())
    return newList    
        
    
if __name__ == '__main__':
    inputfile = raw_input("Enter your input(json): ");
    with codecs.open(inputfile, 'r','utf-8') as data_file:    
        data = json.load(data_file)

    text=data["text"]       
    title=data["title"]
    kc04 = extractKeyphrases(text)
    kt04= extract_title(title)
    
    
    # title + text, n gram.
    
    
    o04=(kt04 + ifin(kc04,kt04) )
    
    string4=makeSingleString(o04)
    
    
    text1 = ""
    text2 = ""
    text3 = ""
    text4 = ""
    text5 = ""
    text6 = ""
    
    title1="Russia plane crash: Dozens killed in Rostov-on-Don"
    title2="Dubai passenger jet crashes in Russia, killing 62 "
    title3="Flydubai plane crashes in Russia; 62 aboard reported dead"
    title5="Could Hillary Clinton's face the same fate as David Petraeus? "
    title6="Istanbul shopping area hit by suicide bomber"

    key1 = extract_title(title1)
    key2 = extract_title(title2)
    key3 = extract_title(title3)
    key5 = extract_title(title5)
    key6 = extract_title(title6)
    key11 = extractKeyphrases(text1)
    key22 = extractKeyphrases(text2)
    key33 = extractKeyphrases(text3)
    key55 = extractKeyphrases(text5)
    key66 = extractKeyphrases(text6)
    
    # extract_title(str)    for title
    # extractKeyphrases(str)    for text
    
    
    o1=(key1 + ifin(key11,key1) )
    o2=(key2 + ifin(key22,key2) )
    o3=(key3 + ifin(key33,key3) )
    o5=(key5 + ifin(key55,key5) )
    o6=(key6 + ifin(key66,key6) )
    
    string1=makeSingleString(o1)
    string2=makeSingleString(o2)
    string3=makeSingleString(o3)
    string5=makeSingleString(o5)
    string6=makeSingleString(o6)
    print(grouping(string4,string2,string3,string5,string6))
    
#print ",".join(toString3(extractKeyphrases(text)))

    """
    print("text1 keywords")
    print key1
    print("text2 keywords")
    print key2
    print("text3 keywords")    
    print key3
    print("text5 keywords")
    print key5
    print("text6 keywords")
    print key6
    
    print("title1 keywords")
    print key1
    print("text1 keywords")
    print key11
    print("title2 keywords")
    print key2
    print("text2 keywords")
    print key22
    print("title3 keywords")    
    print key3
    print("text3 keywords")    
    print key33
    print("title5 keywords")
    print key5
    print("text5 keywords")
    print key55     
    print("title6 keywords")
    print key6      
    print("text6 keywords")
    print key66  
    """
    """
    text7="In October, a Russian charter jet carrying 224 people from Egypt to St. Petersburg crashed in the Sinai desert after an Islamic State-linked terrorist group detonated a homemade bomb aboard the plane"
    key77 = extractKeyphrases(text7)
    print("text7 keywords")
    print key77
    """

    

    
    












