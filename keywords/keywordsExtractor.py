import io
import nltk
from nltk.tokenize import WhitespaceTokenizer
import json
from pprint import pprint
import string
import operator
import codecs


def read_filter_word_file():
    file = codecs.open('./filterWords.txt', )
    redundantList = []
    for line in file:
        if line:
            redundantList.append(line.replace('\n',''))
    return redundantList

#apply syntactic filters based on POS tags         #, 'VBD','VBG','VBN'
def filter_for_tags(tagged, tags=['NN', 'NNP', 'NNS', 'VB']):
    tempList=[item for item in tagged if item[1] in tags]
#     redundantVerb =['be','is','am','are','have','has','had','get']
    redundantVerb = read_filter_word_file()
    
    for item in tempList:
#         print type(item[0])
#         if (item[1] =='VB')and (item[0] in redundantVerb):
#         temp_word = ''
        temp_word = item[0].encode('utf8') #item[0].encode('utf-8')
        for each_word in redundantVerb:
#             cur_each_word = unicode(each_word)
            if temp_word == each_word:
                tempList.remove(item)
                print 'filter_for_tags-> Found junk word, deleted'
                break
    return tempList

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
    output_position = {}
    output_freq = {}
    
    for i in range(len(tokens)):
        if tokens[i] in tagged:
            output_freq.setdefault(tokens[i], 0.0)
            output_position.setdefault(tokens[i], 0.0)
            output_position[tokens[i]]  += position_normal(i+1,len(tokens))
            output_freq[tokens[i]]  += 1
            
    return output_position, output_freq

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
        return 0.5
    elif (normalized > 0.4):
        return 0.6
    elif (normalized > 0.3):
        return 0.7
    elif (normalized > 0.2):
        return 0.8
    elif (normalized > 0.1):
        return 0.9
    elif (normalized > 0):
        return 1.0
    else:
        return 0

def preprocess(text):

    
    redundantList = ['Media caption','Image copyright AFP Image caption ','Image copyright Reuters Image caption ','Image copyright Getty Images']
    
    temp = text                                               
    for item in redundantList:
        temp=temp.replace(item , "")
    
    #remove redundant token "'s" "'t"
    redundantSingleString = ['s','t']        
    #temp_token = nltk.word_tokenize(new_text)
    temp_token = nltk.word_tokenize(temp)
    tokens = []
    for item in temp_token:
        if item not in redundantSingleString:
            tokens.append(item)

    
    '''   ###  no need 
    punctuations = list(string.punctuation)
    punctuations.append("''")
    punctuations.append("``")
    punctuations.remove('-')
    #add space before and behind punctuation 
    new_text = ""
    for t in temp:
        if t not in punctuations:
            new_text= new_text+t
        else:
            new_text= new_text+ " "+t+" " 
    '''
    return tokens 
       
 


def extractKeyphrases(text):
    #tokenize the text using nltk
    tokens = preprocess(text)

    #assign POS tags to the words in the text
    tagged = nltk.pos_tag(tokens)                       #print(tagged)

    #tri- and bi-gram     
    trigram = trigrams(tokens, tagged, 1)  
    bigram  = ifin(bigrams(tokens, tagged, 2),trigram)  

    
    #filter for tags
    filteredtagged = filter_for_tags(tagged) 
    taggedtextlist = [x[0] for x in filteredtagged]
    
    #get the frequency of each token
    positionDict,freqDict  = freq(tokens,taggedtextlist)       #can show key with freq within a range
    
   
    #if it is bi- or tri- gram, increase its position score by .3 or .5
    for item in trigram:
        temp= item.encode("utf-8")
        temp=temp.split()
        for element in temp:
            if element in positionDict:
                positionDict[element] += 0.5
            
    for item in bigram:
        temp= item.encode("utf-8")
        temp=temp.split()
        for element in temp:
            if element in positionDict:
                positionDict[element] += 0.3
    
    
    #sort the freqDict and return a list, smaller no. in front
    sortedList = sorted(positionDict.items(), key=operator.itemgetter(1)) #sortedList=sorted(freqDict.items(), key=lambda t: t[0])
   
    if not sortedList:
        return []
    max = sortedList[-1][1]
    min = sortedList[0][1]
    denominator = max - min
    #normalizedScore = {(token,normalized_score)}
    for i in range(len(sortedList)):
        sortedList[i]=list(sortedList[i])
        if not denominator == 0:
            normalized_position_score = (sortedList[i][1]-min)/ denominator
        else:
            normalized_position_score = 1
        sortedList[i].append(normalized_position_score)
        sortedList[i].append(freqDict[sortedList[i][0]])
        sortedList[i].append(sortedList[i][2]*sortedList[i][3])
        
    #sort by totalscore
    sortedList = sorted(sortedList, key=operator.itemgetter(4))

    # need the last one third of freqDict
    aThird     = (len(sortedList)/3)*2
    freqKey    = sortedList[aThird:]
    
    #uni-grams keywords
    unigram = [each[0] for each in freqKey] 
    unigram.reverse()
    
    return unigram

def ngrams(unigram, bigram, trigram):
    keywords = []
    temp13 = []
    temp12 = []
    temp23 = []
    
    temp13 = ifin(unigram,trigram)
    temp12 = ifin(temp13 ,bigram)
    temp23 = ifin(bigram ,trigram)
    
    keywords.extend(trigram) 
    keywords.extend(temp23) 
    keywords.extend(temp12) 
    return keywords           
               
def extract_title(title): #title

    temp_title= nltk.word_tokenize(title)
    #remove question word for title
    new_title=remove_question_word(temp_title)
    
    #assign POS tags to the words in the title
    tagged_title = nltk.pos_tag(new_title)

    #n-grams keywords
    nnp_tags=["NNP","NN"]
    uni_title= [word[0] for word in tagged_title if word[1] in nnp_tags]
    bi_title=bigrams(new_title,tagged_title,0)
    tri_title = trigrams(new_title,tagged_title,0)
    
    
    output=ngrams(uni_title,bi_title,tri_title)
    return output     


#useless now?    
def toString3(list):
    return ["["+ item +"]" for item in list]     

#useless now?
def grouping(base,list):
    result=[]
    string =""
    for index, item in enumerate(base):
        set0=set(item)
        string = str(index)
        for x,y in enumerate(list,1):
            set1=set(y)
            if len(set0.intersection(set1)) > 9 :
                string=string + "," + str(x)  
        result.append(string)    
    return result

def makeSingleString(list): # remove duplicate already
    temp = []
    for i in list:
        temp.extend(i.split())
    settemp=set(temp)
    newList =[]
    for item in settemp:
        newList.append(item)
    return newList
       
    
if __name__ == '__main__':
    i=0
    key_title=[]
    key_content=[]
    inputfile=['Cuba-Rolling-Stones-rock-Havana-with-landmark-gig.json']#,'Rolling-Stones-make-history-with-free-concert-in-Cuba.json']
    while (i < len(inputfile)):
        #inputfile = raw_input("Enter your input(json)(non_nyt): ");
        with codecs.open(inputfile[i], 'r','utf-8') as data_file:    
            data = json.load(data_file)
     
       # key_title.append(extract_title(data["title"]))
        key_content.append(extractKeyphrases(data["text"]))
        i=i+1
    print(key_content[0])
    #print(key_content[1])
    #print(key_content[2])
    #print(key_content[3])