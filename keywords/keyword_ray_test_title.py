import io
import nltk
from nltk.tokenize import WhitespaceTokenizer
import json
from pprint import pprint
import string
import operator

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
    punctuations.append('“') 
    punctuations.append('”') 
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
    
    text1 = "The FlyDubai Boeing “737-800, coming from Dubai, missed the runway as it attempted to land at 03:50 local time (00:50 GMT) on Saturday. It is not clear what caused the crash but poor visibility and high winds are being considered as a factor. CCTV footage showed an explosion and a huge flash after the plane crashed. The aircraft hit the ground and broke into pieces, the Investigative Committee of Russia said on its website. Reports say the plane abandoned its initial attempt to land and circled for two hours before crashing at the second attempt. It came down about 250m (800ft) short of the start of the runway in Rostov, some 950km (600 miles) south of Moscow. Most of the passengers on board flight FZ981 were Russian, the regional governor said. Another official said three foreigners were on the passenger list, according to Reuters. Six of the crew were non-Russians, a Russian emergency ministry statement said, the news agency reported. About 700 rescue workers were sent to the site of the crash and the fire was extinguished, media reports said. A search is under way for the plane's flight recorders and an investigation has been opened into the cause of the crash. Other flights have been diverted away from the airport. In a statement on its Facebook page, the airliner confirmed the tragic accident and said an emergency response has been put in place. Boeing said on Twitter its team was working to gather more details. FlyDubai, a low cost carrier launched in 2009 with a hub in Dubai, operates flights to some 90 destinations."
    text2 = "MOSCOW — A passenger jet flying from Dubai crashed in southern Russia early Saturday morning, killing all 62 people aboard, Russian officials said  The Boeing 737-800 operated by FlyDubai crashed during a repeated landing attempt in the city of Rostov-on-Don during “poor weather conditions,” Russia's Emergency Ministry announced in a statement  In a second approach in heavy winds, the plane's wing “hit the runway, began to break up, and burst into flames,” the statement read  There were 55 passengers aboard, and seven crew members, according to us Russian officials  Russia's Interfax news wire reported that the plane circled the Rostov airport for 40 to 50 minutes attempting to land in winds reportedly as high as 20 knots  The plane broke up completely on impact, government officials told the newswire Vladimir Markin, the spokesman for the Investigative Committee, said experts have found the cockpit conversation recorder and are continuing the search for another one which records parameters of the flight, the Associated Press reported Russian officials did not appear to suspect foul play or an act of terror immediately following the crash  The country’s Investigative Committee early Saturday morning opened a criminal investigation into any possible safety violations leading to the fatal crash  In October, a Russian charter jet carrying 224 people from Egypt to St  Petersburg crashed in the Sinai desert after an Islamic State-linked terrorist group detonated a homemade bomb aboard the plane “In all likelihood, the cause of the air crash was heavy winds approaching hurricane-strength,” said Vasily Golubev, the governor of the Rostov region, said in remarks broadcast on television early Saturday  The majority of passengers were from the city of Rostov-on-Don and the surrounding region, he said  The Dubai Media Office posted a message on Twiter that said the passengers included 44 people from Russia, eight from Ukraine, two from India and one from Uzbekistan  Russian aviation officials rushed to the site of the crash and President Vladimir Putin ordered government officials to provide aid to the family members of the deceased  More than 600 relatives of passengers aboard the plane have gathered at the Rostov airport, the Interfax news agency reported, citing a press officer at the airport  Rostov-on-Don is in southwestern Russia near the border with Ukraine  Golubev said that there were 55 passengers and seven employees of FlyDubai, the low-cost Saudi airline, aboard the plane  FlyDubai, a budget airline that is the sister carrier to Emirates Airline, was founded in 2008 and now operates more than 1,400 flights a week, according to its website  It has been expanding rapidly into Russia, and flying to Rostov-on-Don since 2013 "
    text3 = "(CNN)After circling a southern Russian airport for more than two hours because of high ground-level winds and poor visibility, a passenger jet from the United Arab Emirates crashed during a landing attempt, killing all 62 people aboard. The flydubai Boeing 737 took off from Dubai and was scheduled to land at the Rostov-on-Don airport at 1:20 a.m. Saturday (6:20 p.m. ET Friday), Russian Emergencies Minister Vladimir Puchkov said. But it didn t come down -- about 800 feet from a runway -- until 3:50 a.m. By that point, Russian state media reported, there were winds of about 60 mph. Authorities have ruled out terrorism as a cause of the crash. Instead, according to investigative committee spokeswoman Oksana Kovrizhnaya, they will be looking at three possibilities: technical issues, severe weather and human error. Kovrizhnaya said the investigations will take at least two months, as required by Russian law, but could be prolonged,  according to state-run Sputnik news. Investigators from UAE, U.S. to join Russian colleagues The plane s pilot had circled the airport hoping the weather would clear, Russia s emergency minister said. After more than two hours, the pilot attempted to land. Instead, the aircraft s tail clipped the ground as it approached Rostov-on-Don s airport, killing all 55 passengers and seven crew members. The  main phase  of the search operation has been completed, said Vladimir Puchkov, the Russian emergencies minister, according to Sputnik news. The search operation is expected to end at 9 a.m. Sunday. The victims  remains have been recovered and sent for forensic analysis, he said.The airport will be closed until Sunday, state-owned news channel Russia-24 quoted officials as saying. Until then, flights are being redirected 141 miles south to the city of Krasnodar. Hundreds of personnel -- from investigators to medics to psychologists on standby to assist grieving family members -- quickly converged on the crash site, and more help is on the way. Four investigators will be coming from the United Arab Emirates, UAE General Civil Aviation Authority official Ismail Al Hosani told reporters in Dubai. And the U.S. National Transportation Safety Board will send a team as well, accompanied by technical advisers from the Federal Aviation Administration and Boeing. Boeing said in a statement it will serve as technical adviser to the investigating authority in charge, the Russian Interstate Aviation Committee. Workers at the crash scene already had both of the plane s flight data recorders and one of two voice recorders by midday Saturday, state-run Ria Novosti reported. 4 children among victims The UAE-based airline said 44 of the passengers were Russians, along with eight Ukrainians, two Indians and one Uzbekistani. Thirty-three of the passengers were women, 18 were men and four were children. Flydubai insisted its primary concern was for the relatives of the victims.  We don t yet know all the details of the accident but we are working closely with the authorities to establish the cause. We are making every effort to care for those affected and will provide assistance to the loved ones of those on board,  flydubai CEO Ghaith Al Ghaith said. A Russian Emergency Situations Ministry employee (L) tries to comfort a relative of the plane crash victims at the Rostov-on-Don airport. Ghaith later told reporters the plane s pilots were  quite experienced,  saying the Cypriot captain had flown 5,965 hours while the Spanish co-captain had flown 5,769 hours. In another statement, the airline said it was contacting families of the victims.  It is a process that will take a little time but as a mark of respect to the families of the bereaved, we want to make every effort to inform them directly prior to releasing the full passenger manifest,  the statement said. Russian President Vladimir Putin expressed his deepest condolences to the families and friends of the victims, state news agency Tass reported. Families of passengers killed will receive 1 million rubles (about $15,000) from the government, Russian state media reported. It said Sunday has been declared a day of mourning in the Rostov administrative region, which borders the Sea of Azov and eastern Ukraine."
    text5 = "Could Hillary Clinton handling of classified information while secretary of state sink her presidential hopes? It s a question that has dogged her campaign for over a year - but opinions are divided over whether the allegations made against her constitute a crime or are just the latest partisan sideshow. Perhaps the best way to look at the implications of her case is by considering the context of another high-profile legal drama involving classified documents that was recently resolved - that of former CIA director David Petraeus. Petraeus pleaded guilty last year to a misdemeanour offence, mishandling classified information, after being accused of handing notebooks with classified information to his biographer-turned mistress, Paula Broadwell. He was fined and placed on probation - a resolution that some have called a slap on the wrist. In other cases people who have revealed classified information were sent to prison. In 2009 Stephen Kim, a former government contractor, was sentenced to 13 months for giving classified material to a reporter. But Petraeus is a high-profile figure. He has been credited with implementing the US military  surge  in Iraq that helped bring stability to the nation - at least temporarily. When President Barack Obama tapped him to head the CIA in 2011, his name was kicked around by some Republicans as a possible presidential candidate in 2012. His celebrated background has led critics to suggest that there is a double-standard in cases involving the mishandling of classified information - one making it less likely that Mrs Clinton will face repercussions for her actions. Mrs Clinton used a private server at her house while she was secretary of state, and some of her emails appeared to have contained classified information, though it s unclear whether that information was classified at the time it was sent. Revealing classified information is a crime. Yet the offence is treated in different ways, depending upon the circumstances. They re also tough cases to prosecute. Government lawyers have to prove an individual knew what he was doing when he revealed classified information, for example, or that she was unusually sloppy when handling the material. After initially denying any culpability, Mrs Clinton has acknowledged that using a private server at her house was a mistake.  I should have used two email addresses, one for personal matters and one for my work at the State Department,  she said on Facebook in September.  I m sorry about it, and I take full responsibility.  One of her former aides, Bryan Pagliano, set up the private server at her house. He has reportedly agreed to co-operate with authorities in the investigation. According to the Washington Post, he s been granted immunity. Officials refused to talk to me on the record about the matter.  I ll leave it to the leakers,  Marc Raimondi, the justice department s national security spokesman says. FBI agents may decide to question Mrs Clinton and more of her aides, both current and former, in the coming months. The danger for Mrs Clinton s presidential campaign, even if she avoids criminal charges, is that it could play into the perception by some that the former secretary of state can t be trusted. For conservatives hoping to defeat her in the general election and break the Democrats  eight-year hold on the Oval Office, that s good news. It also makes any discussion of the legal case fraught with political significance. Every twist and turn in the case, such as revelations this week that one individual had agreed to co-operate with a federal investigation, is scrutinised. Kurt Volker, a former US ambassador who s now executive director of the McCain Institute, says her actions are potentially worse than anything Petraeus did. Though Petraeus willingly revealed classified information to his mistress, Mrs Clinton apparently sent email with classified information through a server without proper safeguards. As Volker sees things, the classified material became vulnerable to hackers. Everybody and their uncle can potentially see that information, he says. That means Iranians, Chinese, whoever. Volker believes she should be punished for her actions and that investigators are doing the right thing in their efforts to find out more about the case. But he s sceptical about the outcome. He believes that during an election year, with a Democratic administration in power, she s unlikely to be held accountable for what she did. FBI agents will pursue it as a criminal matter, he says, but he believes that justice department officials will  take into account the political context  (and that Mrs Clinton is a Democratic candidate for the presidency.) His suspicions about political bias in the White House reinforce a universal truth - campaign season is a time of passion, paranoia and fiery rhetoric. Few in Washington think that formal charges will be brought against her, however. And if they were, it s hard to see how she d be sent to prison for committing the same kind of crime for which Petraeus received probation. If she is charged and avoids any serious penalty, then FBI agents, federal investigators - and plenty of her political adversaries - would have reason to be angry.  But as far as I can see no crimes have been committed,  says Steven Aftergood, the director of the Project on Government Secrecy for the Federation of American Scientists.  So I don t see a place for that sort of frustration.  Like Volker, he sees the issue as political.  We ve been bombarded with accusations before any indictment has been filed,  Aftergood says.  And for that reason it seems like a manufactured controversy.  And however you see the politics surrounding the case of Mrs Clinton s email, the controversy is bound to continue - at least until the election."
    text6 = "A suicide bomb attack at a busy shopping area in the Turkish city of Istanbul has killed at least four people, officials say. Up to 20 people were injured, three seriously. The area - Istiklal Street - is reportedly crowded at weekends. Last Sunday, an attack in the capital, Ankara, killed 37 people. Kurdish rebel group TAK claimed that attack, saying it was in revenge for Turkish military operations against Kurds. Last month, a bomb attack on a military convoy in Ankara killed 28 people and wounded dozens more. In October 2015, more than 100 people were killed in a double-suicide bombing at a Kurdish peace rally in Ankara. The attack in Istanbul - Turkey's largest city - occurred around 11:00 (09:00 GMT). Uwes Shehadeh was some 500m away when he heard a horrific and horrible noise. People didn't know what was going on. It was very chaotic. Everyone was screaming and running away, he told the BBC.  Istanbul is on high alert and people are very worried as to what will happen next. Three Israeli tourists were among those injured, local media report say. The Israeli foreign ministry has confirmed Israelis were wounded, but not given the number or said what condition they are in. Both the so-called Islamic State (IS) and Kurdish militants have claims recent attacks in Turkey. President Recep Tayyip Erdogan has said terror groups are targeting civilians because they are losing their struggle against Turkish security forces. Turkey is part of the US-led coalition against IS and allows coalition planes to use its air base at Incirlik for raids on Iraq and Syria. It has also been carrying out a campaign of bombardment against Syrian Kurdish fighters of the People's Protection Units (YPG), which it regards as a extension of the outlawed Kurdistan Workers Party (PKK). A two-year-old ceasefire between Turkey and the PKK broke down last summer. Since then, more than 340 members of Turkey's security forces have been killed along with at least 300 Kurdish fighters and more than 200 civilians. The TAK (Kurdistan Freedom Hawks) was formed in 2004. It is regarded as the hard-line offshoot of the PKK, rejecting any attempt at ceasefire talks with the Turkish state. The PKK has been fighting for autonomy for Turkey's Kurdish minority for decades and has carried out regular attacks on Turkish security forces. "
    
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
    print(grouping(string1,string2,string3,string5,string6))
   
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

    

    
    












