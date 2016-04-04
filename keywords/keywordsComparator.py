import serverConfiguration
from nltk.corpus import wordnet as wn
from nltk.corpus import wordnet_ic
brown_ic = wordnet_ic.ic('ic-brown.dat')
semcor_ic = wordnet_ic.ic('ic-semcor.dat')
from nltk.corpus import genesis
genesis_ic = wn.ic(genesis, False, 0.0)
import keywordsComparator
import time



##################################################################################
#    Global variable
#    Keywords checking timeout, in second, normally, longer time gives more precise answer
keywords_checking_timeout = serverConfiguration.keywords_checking_timeout


##################################################################################
def abs_value(val):
    if val<0:
        return -val
    return val
def title_similarity(t1, t2, s1, s2):
    
    tlist1 = string_to_wordlist(t1)
    tlist2 = string_to_wordlist(t2)
    num_max = max([len(tlist1), len(tlist2)])
    if num_max == 0:
        return False
    strong_num = 0
    for each1 in tlist1:
        for each2 in tlist2:
            a = keywordsComparator.sim_all_cal(each1, each2)
            if a >=0.7:
                strong_num += 1
    if (strong_num / (num_max) ) > 0.7:
        print 'title_similarity-> Title check returns TRUE'
        return True
    
    
    wlist1 = string_to_wordlist(s1)
    wlist2 = string_to_wordlist(s2)
#     print wlist1
#     print wlist2
    num_max = max([len(wlist1), len(wlist2)])
    if num_max == 0:
        return False
    strong_num = 0
    for each1 in wlist1:
        for each2 in wlist2:
            a = keywordsComparator.sim_all_cal(each1, each2)
            if a >=0.7:
#                 print 'The similar words in title are ', each1, ' and ', each2, ' @ ', a
                strong_num +=1
#     print 'strong_num is ', strong_num, ' and num_max is ', num_max
#     print
#     if num_max = 0:
#         return False
#     print 'The debug data is S.N ', strong_num,' div ', num_max, ' @ ', s1,' AND ', s2
    if (strong_num / (num_max+2) ) > 0.7:
        print 'title_similarity-> Keywords check returns TRUE'
        return True
    return False
           
def cal_similarity(s1, s2):
    #    First 3 words are location, following words are title + content
    
    
    wlist1 = string_to_wordlist(s1)
    wlist2 = string_to_wordlist(s2)
    num_word = len(wlist1) + len(wlist2)
    com_word = len(wlist1) * len(wlist2)
    if com_word > 400:
        com_word = 400
#     num_max = max(len(wlist1) / len(wlist2), len(wlist2) / len(wlist1))
    strong_num = 0
    total_score = 0
    
    w1_count = 0
    w2_count = 0
    
    timeout = time.time() + keywords_checking_timeout
    cal_count = 0
    for each1 in wlist1:
        for each2 in wlist2:
        
            word_multiplier = 1.0
            if (w1_count < 3) or (w2_count < 3):
                if (w1_count < 3):
                    break
                if (w2_count < 3):
                    w2_count+=1
                    continue
#                 word_multiplier = 2.0
            elif (w1_count < 10) or (w2_count < 10):
                word_multiplier = 3.0
            elif (w1_count > 30) or (w2_count > 30):
                word_multiplier = 0.5
            word_multiplier *= (w1_count+1) / (w2_count+1)
            a = keywordsComparator.sim_all_cal(each1, each2)
            cal_count+=1
            if a >= 1.0:
                total_score += word_multiplier * a * 60.0# * 100 / num_word
                strong_num += 2
            elif a>0.8:
                strong_num += 1
                total_score += word_multiplier * a * 40.0 #* 100 / num_word
            elif a>0.6:
                total_score += word_multiplier * a * 10.0
            else:
                total_score += word_multiplier * a * 1.0
            w2_count += 1
            if w2_count > 40:
                break
        w2_count = 0
        w1_count +=1
        if w1_count > 40:
            break
#         if time.time() > timeout:
#                 print 'cal_similarity-> Timeout for this artilce, escape the calculation @ ', cal_count, 'times calculation'
#                 break
    print 'cal_similarity-> Finish calculation @ ', cal_count, 'times calculation'
#     return total_score * strong_num / com_word
    if com_word > cal_count:
        com_word = cal_count
    return total_score / com_word #(len(wlist1) + len(wlist2))



def fast_compare(s1, s2, g1, g2):
    wlist1 = string_to_wordlist(s1)
    wlist2 = string_to_wordlist(s2)
    geolist1 = string_to_wordlist(g1)
    geolist2 = string_to_wordlist(g2)
    num_word = min(len(wlist1), len(wlist2))
    same_word_count = 0
    same_geo_count = 0
    for each1 in wlist1:
        if each1 in wlist2:
            same_word_count += 1
    if same_word_count >=(int(num_word/10)+2):
        print 'fast_compare->Fast comparator (KEYWORDS) returns TRUE, @ ', same_word_count, ' words similar, continue this article'
        return True
    
    for each1 in geolist1:
        if each1 in geolist2:
            print 'fast_compare->Fast comparator (GEOLOCATION) returns TRUE, continue this article'
            return True
    
    
    a =0.0
    short_list_1 = []
    short_list_2 = []
#     index = 0
#     for each in wlist1:
#         short_list_1.append(each)
#         if index == 2:
#             break
#         index+=1
#     index = 0
#     for each in wlist2:
#         short_list_1.append(each)
#         if index == 2:
#             break
#         index +=1
    if len(wlist1)<6 or len(wlist2)<6:
        print 'fast_compare->Fast comparator (INSUFFICIENT) returns TRUE, continue this article'
        return True
    short_list_1 = [wlist1[3],wlist1[4],wlist1[5]]#,wlist1[3],wlist1[4]]
    short_list_2 = [wlist2[3],wlist2[4],wlist2[5]]#,wlist2[3],wlist2[4]]
    wup_count = 0
    for each1 in short_list_1:
        for each2 in short_list_2:
           if wup_sim_cal(each1, each2) > 0.7:
               wup_count += 1
    if wup_count > 2:
        print 'fast_compare->Fast comparator (WUP CAL) returns TRUE, continue this article'
        return True
    print 'fast_compare->Fast comparator returns False, skip this article!!!!!!'
    return False



#    Make string to list, by skipping ",", last string is ignored
#    Eliminating duplicated key
def string_to_wordlist(str):
    words = str.split(",")
    words.pop()
    unique_words = []
    data_words = []
    for each in words:
        for each1 in each.split():
            data_words.append(each1)
    for each in data_words:
#         if not each in unique_words:
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
    score /= 22
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
    
    
    
