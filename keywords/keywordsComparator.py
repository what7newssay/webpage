from nltk.corpus import wordnet as wn
from nltk.corpus import wordnet_ic
brown_ic = wordnet_ic.ic('ic-brown.dat')
semcor_ic = wordnet_ic.ic('ic-semcor.dat')
from nltk.corpus import genesis
genesis_ic = wn.ic(genesis, False, 0.0)
import keywordsComparator

def title_similarity(s1, s2):
    wlist1 = string_to_wordlist(s1)
    wlist2 = string_to_wordlist(s2)
#     print wlist1
#     print wlist2
    num_max = max(len(wlist1), len(wlist2))
    strong_num = 0
    for each1 in wlist1:
        for each2 in wlist2:
            a = keywordsComparator.sim_all_cal(each1, each2)
            if a >=0.7:
                print 'The similar words in title are ', each1, ' and ', each2, ' @ ', a
                strong_num +=1
    print 'strong_num is ', strong_num, ' and num_max is ', num_max
    print
    if (strong_num / num_max ) > 0.7:
        return True
    return False
           
def cal_similarity(s1, s2):
    wlist1 = string_to_wordlist(s1)
    wlist2 = string_to_wordlist(s2)
    num_word = len(wlist1) + len(wlist2)
    com_word = len(wlist1) * len(wlist2)
#     num_max = max(len(wlist1) / len(wlist2), len(wlist2) / len(wlist1))
    strong_num = 0
    total_score = 0
    for each1 in wlist1:
        for each2 in wlist2:
            a = keywordsComparator.sim_all_cal(each1, each2)
            if a >= 1.0:
                total_score += a * 50.0 #* 60 / num_word
                strong_num += 3
                break
            if a>0.8:
                strong_num += 1
                total_score += a * 30.0 #* 15 / num_word
            elif a>0.6:
                total_score += a * 20.0
            else:
                total_score += a * 1.0
    return total_score * strong_num / (((num_word  - strong_num)+0.1)/2) / com_word#(len(wlist1) + len(wlist2))

#    Make string to list, by skipping ",", last string is ignored
def string_to_wordlist(str):
    words = str.split(",")
    words.pop()
    unique_words = []
    data_words = []
    for each in words:
        for each1 in each.split():
            data_words.append(each1)
    for each in data_words:
        if not each in unique_words:
            unique_words.append(each)
    return unique_words

#    To calculate weighted score of word pair
def sim_all_cal(word1, word2):
    if len(word1) ==0 or len(word2)==0:
        return 0.0
    if word1 == word2:
        return 1.0
    score = 0.0
    lch = keywordsComparator.lch_sim_cal(word1, word2)
    
#     print ("This is lch_sim_cal value: ", lch)
    
    wup = keywordsComparator.wup_sim_cal(word1, word2)
    
#     print ("This is wup_sim_cal value: ", wup)
    
    lin = keywordsComparator.lin_sim_cal(word1, word2)
#     print ("This is lin_sim_cal value: ", lin)
    
#     jcn_g = keywordsComparator.jcn_genesis_sim_cal(word1, word2)
#     print ("This is jcn_genesis_sim_cal value: ", jcn_g)
    
#     jcn_b = keywordsComparator.jcn_brown_sim_cal(word1, word2)
#     print ("This is jcn_brown_sim_cal value: ", jcn_b)
    
    path = keywordsComparator.path_sim_cal(word1, word2)
#     print ("This is path_sim_cal value: ", path)

    score += lch * 6
    score += wup * 10
    score += lin * 4
#     score += jcn_g * 1
#     score += jcn_b * 1
    score += path * 2
    score /= (24 -2)
    return score


#    LCH similarity calculation, 2nd
def lch_sim_cal(word1, word2):
    list = []
    w1 = wn.synsets(word1, pos=wn.VERB)
    w2 = wn.synsets(word2, pos=wn.VERB)
    for each1 in w1:
        for each2 in w2:
            s = each1.lch_similarity(each2)
            list.append(s)
            if s>3.0:
                return 1.0
    w1 = wn.synsets(word1, pos=wn.NOUN)
    w2 = wn.synsets(word2, pos=wn.NOUN)
    for each1 in w1:
        for each2 in w2:
            s = each1.lch_similarity(each2)
            list.append(s)
            if s>3.0:
                return 1.0
    if not list:
        return 0.0
    a = max(list, 0.0)
    if a>3:
        return 1.0
    elif a>2.5:
        return 0.8
    elif a>2.0:
        return 0.6
    elif a>1.5:
        return 0.4
    elif a>1:
        return 0.2
    elif a>=0:
        return 0

#    WUP similarity calculation, 1st
def wup_sim_cal(word1, word2):
    list = []
    wordFromList1 = wn.synsets(word1)
    wordFromList2 = wn.synsets(word2)
    if wordFromList1 and wordFromList2: 
        for each1 in wordFromList1:
            for each2 in wordFromList2:
                a = each1.wup_similarity(each2)
                list.append(a)
                if a >=1.0:
                    return 1.0
    if not list:
        return 0.0
    list.append(0.0)
    a= max(list)
    return a


#    LIN similarity calculation, 3rd
def lin_sim_cal(word1, word2):
    list = []
    w1 = wn.synsets(word1, pos=wn.VERB)
    w2 = wn.synsets(word2, pos=wn.VERB)
    for each1 in w1:
        for each2 in w2:
            s = each1.lin_similarity(each2, semcor_ic)
            list.append(s)
            if s ==1.0:
                return s
    
    
    w1 = wn.synsets(word1, pos=wn.NOUN)
    w2 = wn.synsets(word2, pos=wn.NOUN)
    for each1 in w1:
        for each2 in w2:
            s = each1.lin_similarity(each2, semcor_ic)
            list.append(s)
            if s ==1.0:
                return s
    if not list:
        return 0.0
    list.append(0.0)
    a = max(list)
    return a

#    JCN brown similarity calculation, 6th
def jcn_brown_sim_cal(word1, word2):
    list = []
    w1 = wn.synsets(word1, pos=wn.VERB)
    w2 = wn.synsets(word2, pos=wn.VERB)
    for each1 in w1:
        for each2 in w2:
            s = each1.jcn_similarity(each2, brown_ic)
            list.append(s)
            if s >=3.0:
                return 1.0
    
    
    w1 = wn.synsets(word1, pos=wn.NOUN)
    w2 = wn.synsets(word2, pos=wn.NOUN)
    for each1 in w1:
        for each2 in w2:
            s = each1.jcn_similarity(each2, brown_ic)
            list.append(s)
            if s >=3.0:
                return 1.0
    if not list:
        return 0.0
    a = max(list, 0.0)
    if a>3:
        return 1.0
    elif a>2.5:
        return 0.8
    elif a>2.0:
        return 0.6
    elif a>1.5:
        return 0.4
    elif a>1:
        return 0.2
    elif a>=0:
        return 0

#    JCN genesis similarity calculation, 5th
def jcn_genesis_sim_cal(word1, word2):
    list = []
    w1 = wn.synsets(word1, pos=wn.VERB)
    w2 = wn.synsets(word2, pos=wn.VERB)
    for each1 in w1:
        for each2 in w2:
            s = each1.jcn_similarity(each2, genesis_ic)
            list.append(s)
            if s >=3.0:
                return 1.0
    
    w1 = wn.synsets(word1, pos=wn.NOUN)
    w2 = wn.synsets(word2, pos=wn.NOUN)
    for each1 in w1:
        for each2 in w2:
            s = each1.jcn_similarity(each2, genesis_ic)
            list.append(s)
            if s >=3.0:
                return 1.0
    if not list:
        return 0.0
    a = max(list, 0.0)
    if a>3:
        return 1.0
    elif a>2.5:
        return 0.8
    elif a>2.0:
        return 0.6
    elif a>1.5:
        return 0.4
    elif a>1:
        return 0.2
    elif a>=0:
        return 0
 
#    PATH similarity calculation, 4th
def path_sim_cal(word1, word2):
    list = []
    w1 = wn.synsets(word1, pos=wn.VERB)
    w2 = wn.synsets(word2, pos=wn.VERB)
    for each1 in w1:
        for each2 in w2:
            s = each1.path_similarity(each2)
            list.append(s)
#             if s >=3.0:
#                 return 1.0
    
    
    w1 = wn.synsets(word1, pos=wn.NOUN)
    w2 = wn.synsets(word2, pos=wn.NOUN)
    for each1 in w1:
        for each2 in w2:
            s = each1.path_similarity(each2)
            list.append(s)
#             if s >=3.0:
#                 return 1.0
    if not list:
        return 0.0
    list.append(0.0)
    a = max(list)
    return a
#     if a>3:
#         return 1.0
#     elif a>2.5:
#         return 0.8
#     elif a>2.0:
#         return 0.6
#     elif a>1.5:
#         return 0.4
#     elif a>1:
#         return 0.2
#     elif a>=0:
#         return 0
    
    
    
