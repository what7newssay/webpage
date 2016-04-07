import grouping
import keywordsExtractor

#############################################################################
# Grouping test
# testID1 = '00a89e8471a9477883af912795416c37'
# testID2 = '37cc07ac33e04e8baaf79f0cad7e084c'
# testTopicID = '8ca812a47a0f4958b9d7fafe544735f8'

# grouping.compare_two_art(testID1,testID2)
# grouping.compare_art_group(testID1,testTopicID)

#############################################################################

def get_all_words():
    print 'get_all_words-> Starting'
    all_art_list = grouping.get_all_art()
#     print all_art_list
    word_data = []
    art_count = 0
    for each_art in all_art_list:
        art_key_com = each_art[4]
        art_key_list = art_key_com.split(',')
        art_count += 1
        print 'get_all_words-> (Processing) No. ', art_count, ' article.'
        for each_word in art_key_list:
            if not each_word:
                continue
            cur_word = each_word
            found_enrty = False
            for each_entry in word_data:
                if each_entry[0] == cur_word:
                    each_entry[1] += 1
                    found_enrty = True
                    break
            if not found_enrty:
                newlist = [cur_word, 1]
                word_data.append(newlist)
        word_data.sort(key = lambda x:(-x[1],x[0]))
        
        
        if art_count %100 ==0:
            print 'Delete junk word'
            for each in word_data:
                if each [1] <= 1:
                    word_data.remove(each)

    count = 0
    for each in word_data:
        print 'The ', count + 1, ' position word is', each
        print each[0]
        if count > 100:
            break
        count += 1

if __name__ == '__main__':
    get_all_words()
#     s1 = unicode('be')
#     s2 = 'be'
#     print s1
#     print s2
#     print s1==s2
#     str1 = ['be', 'my', 'fucking', 'program']
#     for each in str1:
#         if each in keywordsExtractor.read_filter_word_file():
#             str1.remove(each)
#     print str1
#     list = keywordsExtractor.read_filter_word_file()
#     print type(list[0])
#     print 'End of Function, test.py'