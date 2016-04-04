from nltk.corpus import wordnet as wn
from nltk.corpus import wordnet_ic
from datetime import date
brown_ic = wordnet_ic.ic('ic-brown.dat')
semcor_ic = wordnet_ic.ic('ic-semcor.dat')
from nltk.corpus import genesis
genesis_ic = wn.ic(genesis, False, 0.0)
import keywordsComparator
import mysql.connector
import datetime
import serverConfiguration

#################################################################################
# Database variable
DBuser =  serverConfiguration.DBuser
DBpass = serverConfiguration.DBpass
DBhost = serverConfiguration.DBhost

# Similarity variable
similarity_value_rough = serverConfiguration.similarity_value_rough
similarity_value_precise = serverConfiguration.similarity_value_precise
#################################################################################

def get_group_art():
    cnx =  mysql.connector.connect(user = DBuser, password = DBpass,
                                 host = DBhost,
                                 database='NewsDatabase')
    print "get_art_DB->Database connection successful!"
    newsDBcursor = cnx.cursor()
    checkQuery = ("""SELECT * FROM originalArt WHERE (topicID != '"UNDEFINE"' AND topicID != 'FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF');""")
    newsDBcursor.execute(checkQuery)
    selectData = newsDBcursor.fetchall()
    cnx.close()
    return selectData

def get_all_art():
    cnx =  mysql.connector.connect(user = DBuser, password = DBpass,
                                 host = DBhost,
                                 database='NewsDatabase')
    print "get_all_art->Database connection successful!"
    newsDBcursor = cnx.cursor()
    checkQuery = ("""SELECT * FROM originalArt;""")
    newsDBcursor.execute(checkQuery)
    selectData = newsDBcursor.fetchall()
    cnx.close()
    return selectData

def get_topic_art(topicID):
    cnx =  mysql.connector.connect(user = DBuser, password = DBpass,
                                 host = DBhost,
                                 database='NewsDatabase')
    print "get_art_DB->Database connection successful!"
    newsDBcursor = cnx.cursor()
    checkQuery = ("""SELECT * FROM summarizedArt WHERE topicID = %s;""")
    dataQuery = (topicID,)
    newsDBcursor.execute(checkQuery, dataQuery)
    selectData = newsDBcursor.fetchall()
    cnx.close()
    return selectData

def get_art_DB(uniqueID):
    cnx =  mysql.connector.connect(user = DBuser, password = DBpass,
                                 host = DBhost,
                                 database='NewsDatabase')
    print "get_art_DB->Database connection successful!"
    newsDBcursor = cnx.cursor()
    checkQuery = ("""SELECT * FROM originalArt WHERE uniqueID = %s;""")
    newsDBcursor.execute(checkQuery, (uniqueID,))
    selectData = newsDBcursor.fetchone()
    cnx.close()
    return selectData

def get_art_summarizedArt(uniqueID):
    cnx =  mysql.connector.connect(user = DBuser, password = DBpass,
                                 host = DBhost,
                                 database='NewsDatabase')
    print "get_art_summarizedArt->Database connection successful!"
    newsDBcursor = cnx.cursor()
    checkQuery = ("""SELECT * FROM summarizedArt WHERE uniqueID = %s;""")
    newsDBcursor.execute(checkQuery, (uniqueID,))
    selectData = newsDBcursor.fetchone()
    cnx.close()
    return selectData

def get_other_art(art_list):
    #    Get article list from originalArt table only if it is not in art_list
    #    Datastructure in art_list:
    #    [uniqueID,uniqueID,......] all members are uniqueID
    get_list =[]
    cnx =  mysql.connector.connect(user = DBuser, password = DBpass,
                                 host = DBhost,
                                 database='NewsDatabase')
    print "get_ungroup_art->Database connection successful!"
    newsDBcursor = cnx.cursor()
    checkQuery = ("""SELECT * FROM originalArt;""")
    newsDBcursor.execute(checkQuery)
    selectData = newsDBcursor.fetchall()
    cnx.close()
    for each in selectData:
        if not (each[0] in art_list):
            get_list.append(each)
    
    return get_list

def get_ungroup_art(force_group):
    #    Get all articles that is ungrouped or nogroup
    #    With TRUE parameter: all no group articles will be forced to check for new group
    #    With FALSE parameter: all new articles will be checked for group
    cnx =  mysql.connector.connect(user = DBuser, password = DBpass,
                                 host = DBhost,
                                 database='NewsDatabase')
    print "get_ungroup_art->Database connection successful!"
    newsDBcursor = cnx.cursor()
    if force_group:
        checkQuery = ("""SELECT * FROM originalArt WHERE (topicID = '"UNDEFINE"' OR topicID = 'FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF');""")
    else:
        checkQuery = ("""SELECT * FROM originalArt WHERE topicID = '"UNDEFINE"';""")
    newsDBcursor.execute(checkQuery)
    selectData = newsDBcursor.fetchall()
    cnx.close()
    return selectData

def find_sim_art(selectData):
    #    Find similar articles in selectData
    #    selectData is full table of originalArt
    #    The datastructure is the same as in originalArt table
    #    This will set no group articles to no group: i.e. the topicID will be set to FFFFFFFF
    #    Return art_list that contains similar articles
    selectData_to = list(selectData)
    selectData_to.pop(0)
    art_list = []
    total_num_art = len(selectData)*len(selectData)
    index = 0
    for index,each1 in enumerate(selectData, start=0):
        w1 = each1[6] + each1[3] + each1[4]
        for index1,each2 in enumerate(selectData_to, start=index):
            cur_art = []
            if each1[0] == each2[0]:
                print 'find_sim_art (First loop)-> Same uniqueID skip this article!'
                continue
            
            if keywordsComparator.title_similarity(each1[1], each2[1], each1[3], each2[3]) and (each1[0] != each2[0]):
                total_num_art -= 1
#                 print 'The articles with similar title, same!!!>>>>>>>>>>>>>>>>'
#                 print 'The title is ', each1[1], ' and ', each2[1]
                cur_art = [each1[0],each2[0],5000]
                art_list.append(cur_art)
                continue
            w2 = each2[6] + each2[3] + each2[4]
            location1 = each1[6]
            location2 = each2[6]
            if not keywordsComparator.fast_compare(w1, w2, location1, location2):
                continue
            
            a = keywordsComparator.cal_similarity(w1, w2)
            ######################################################################################################
            if a >= similarity_value_rough:
                print 'find_sim_art-> (First Loop) This article IS similar wtih weighted score is: ', a, "for ", w1
                print " and ", w2
                cur_art = [each1[0],each2[0],a]
                art_list.append(cur_art)
            else:
                print 'find_sim_art-> (First Loop) This article is NOT similar with weighted score is: ', a, "for ", w1
                print " and ", w2  
            
            ######################################################################################################
            if (total_num_art % 20 ==0):
                print "Remaining articles ", total_num_art
            total_num_art -= 1
            index += 1
        if len(art_list)==0:
            update_nogroup_art(each1[0])
            if len(selectData_to) >= 2:
#                 selectData.pop(0)
                selectData_to.pop(0)
                continue
            else:
                break
        break
    # Finish finding similar articles, as 1st reference
    if len(art_list) ==0:
        return art_list
    
    print 'Starting find deeper similar articles'
    
    #    art_list should be [[topicID, uniqueID, value],[topicID, uniqueID, value],..]
    
    ID_list = []
    ID_list.append(art_list[0][0])
    for each in art_list:
        ID_list.append(each[1])
    otherArt_list = get_other_art(ID_list)
    if len(otherArt_list) ==0:
        return art_list
    
    print '*************************************find_sim_art ( Mid ID_list)'
    for each in ID_list:
        print each
    print '************************************************'
    print '*************************************find_sim_art ( Mid ID_list)'
    topicID = ID_list[0]
#     print topicID
    print
#     print '*************************************find_sim_art ( Mid otherArt_list)'
#     for each in otherArt_list:
#         print each
#         print '************************************************'
#     print '*************************************find_sim_art ( Mid otherArt_list)'
    print 
    print otherArt_list
   
    print '****************************************************'
    print '*************************************find_sim_art ( Mid art_list)'
    for each in art_list:
        print each
        print '************************************************'
    print '*************************************find_sim_art ( Mid art_list)'
    for each1 in ID_list:
        this_art = get_art_DB(each1)
        for each2 in otherArt_list:
            cur_art = []
            w1 = this_art[6] + this_art[3] + this_art[4]
            w2 = each2[6] + each2[3] + each2[4]
            location1 = this_art[6]
            location2 = each2[6]
            if not keywordsComparator.fast_compare(w1, w2, location1,location2):
                continue
            
            if keywordsComparator.title_similarity(this_art[1], each2[1], this_art[3], each2[3]) and (this_art[0] != each2[0]):
#               print 'The articles with similar title, same!!!>>>>>>>>>>>>>>>>'
#               print 'The title is ', each1[1], ' and ', each2[1]
                cur_art = [topicID,each2[0],5000]
                art_list.append(cur_art)
                otherArt_list = remove_art_from_list(each2[0],otherArt_list)
                continue
            a = keywordsComparator.cal_similarity(w1, w2)
            ######################################################################################################
            if a >= similarity_value_precise:
                print 'find_sim_art-> (Second Loop) This article IS additional similar with weighted score is: ', a, "for ", w1
                print " @and@ ", w2
                cur_art = [topicID,each2[0],a]
                art_list.append(cur_art)
                otherArt_list = remove_art_from_list(each2[0],otherArt_list)
            else:
                print 'find_sim_art-> (Second Loop) This article is NOT additional similar with weighted score is: ', a, "for ", w1
                print " @and@ ", w2
            ######################################################################################################
            
               
    # Debug only
    print '*************************************find_sim_art (Last - before)'
    for each in art_list:
        print '*************************************'
        print   
        print each
        print
        print
    print '**************************************'
    
    #    The following codes are used to refine the art_list
#     artID_list = []
#     artID_list.append(art_list[0][0])
#     for each in art_list:
#         artID_list.append(each[1])
#     
    
    return art_list


def remove_art_from_list(artID,artList):
    #    Remove a article based on artID (uniqueID), as long as each in artList
    #    contains each[0] as uniqueID, then usable
    result = []
    switcher = True
    for each in artList:
        if artID == each[0]:
            switch = False
            continue
        result.append(each)
    if switcher:
        print 'remove_art_from_list no such element find', artID
    return result


def recal_sim_group(art_list):
    #    Recalculate all similarities between articles in art_list
    #    
    #    Datastructure in art_list
    #    [topicID, uniqueID, similarityValue]
    result_list = list(art_list)
    process_list = []
    if len(art_list)<=1 :
        update_group_art(result_list)
        return result_list
#     process_list.append(get_art_DB(art_list[0][0]))
    value_arr = []
    for each in art_list:
        process_list.append(get_art_DB(each[1]))
        value_arr.append(each[2])
    result_list.append([art_list[0][0],art_list[0][0],max(value_arr)])
    print 'There are ',len(process_list),' news waiting for recalculation process'
    process_list_to = list(process_list)
    print process_list
#     process_list_to.pop(0)
    process_count = 0
    
    #    Debug only
    #######################################################################
    print '#####################################################->recal_sim_group (Fisrt Debug)'
    for each in result_list:
        print each
        print '##########################################################'
    print '##############################################################'
    #######################################################################
    for each1 in process_list:
        value_arr[:] = []
        avg_arr =  []
        ori_value = result_list[process_count][2]
        for each2 in process_list:
            if each1[0] == each2[0]:
                print 'Same uniqueID: ',each1[0],' and ',each2[0]
                continue
            if keywordsComparator.title_similarity(each1[1], each2[1], each1[3], each2[3]) and (each1[0] != each2[0]):
                print 'recal_sim_group-> Same title detection @ ', each1[0]
                print 'and ', each2[0]
                value_arr.append(5000)
                avg_arr.append(similarity_value_precise * 1.5)
                break
            w1 = each1[6] + each1[3] + each1[4]
            w2 = each2[6] + each2[3] + each2[4]
            a = keywordsComparator.cal_similarity(w1, w2)
            print 'Did calculation at ',each1[0],' and ',each2[0],' @ ',a
            value_arr.append(a)
            avg_arr.append(a)
        value_arr.append(result_list[process_count][2])
        avg_arr.append(result_list[process_count][2])
        print value_arr
        max_value = max(value_arr)
        avg_value = sum(avg_arr)/(float(len(avg_arr)))
        
        if avg_value < similarity_value_rough:
            result_list[process_count][2] = -1
        else:
            result_list[process_count][2] = max_value
        ###################################################################################
#         if ori_value == max_value and max_value<similarity_value_rough:
#             result_list[process_count][2] = -1
#         else:
#             result_list[process_count][2] = max_value
        ###################################################################################
        process_count+=1  
        
        # For loop
#     print result_list
    update_group_art(result_list)
    return result_list
    
    
def update_group_art(art_list):
    #    Update the database base base on art_list
    #    The data structure in art_list
    #    [[topicID,uniqueID,similarityValue],[topicID,uniqueID,similarityValue],..]
    #    usually lead article, the article with uniqueID itself as topicID, is not included in art_list
    #    update the lead article first
    if not art_list:
        #    If there is no articles to update, return
        return
    
    cnx =  mysql.connector.connect(user = DBuser, password = DBpass,
                                 host = DBhost,
                                 database='NewsDatabase')
    print "update_group_art->Database connection successful!"
    newsDBcursor = cnx.cursor()
    
    # Debug only
#     print '*************************************'
#     for each in art_list:
#         print '*************************************'
#         print   
#         print each
#         print
#         print
#     print '**************************************'
    checkQuery = ("""UPDATE summarizedArt SET topicID= %s, similarity = %s, updateDate = CURDATE() WHERE uniqueID = %s;""")
    dataQuery = (art_list[0][0],art_list[0][2],art_list[0][0])
    try:
        newsDBcursor.execute(checkQuery, dataQuery)
        cnx.commit()
        print 'update_group_art-> Update summarizedArt for main topic holder successful! @ ', art_list[0][0]
        
    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err))
        print 'update_group_art -> Update summarizedArt for main topic holder FAILED!!!!!'
    
    checkQuery = ("""UPDATE originalArt SET topicID= %s WHERE uniqueID = %s;""")
    dataQuery = (art_list[0][0],art_list[0][0])
    try:
        newsDBcursor.execute(checkQuery, dataQuery)
        cnx.commit()
        print 'update_group_art-> Update originalArt for main topic holder successful! @ ', art_list[0][0]
    except mysql.connector.Error as e:
        print 'update_group_art -> Update originalArt for main topic holder FAILED!!!!!'
    
    
    newsDBcursor = cnx.cursor()
    for each in art_list:
        if each[2] <0:
            continue
        checkQuery = ("""UPDATE summarizedArt SET topicID= %s, similarity = %s, updateDate = CURDATE() WHERE uniqueID = %s;""")
        dataQuery = (each[0],each[2],each[1])
        try:
            newsDBcursor.execute(checkQuery, dataQuery)
            cnx.commit()
            print 'update_group_art-> Update summarizedArt successful! @ ', each[1]
        except mysql.connector.Error as e:
            print("Something went wrong: {}".format(e))
            print 'update_group_art -> Update summarizedArt for art_list member\'s topic  FAILED!!!!!'
            print '@ ', each[1]
        
        checkQuery = ("""UPDATE originalArt SET topicID= %s WHERE uniqueID = %s;""")
        dataQuery = (each[0],each[1])
        try:
            newsDBcursor.execute(checkQuery, dataQuery)
            cnx.commit()
            print 'update_group_art-> Update originalArt successful! @ ', each[1]
        except mysql.connector.Error as e:
            print("Something went wrong: {}".format(e))
            print 'update_group_art -> Update originalArt for art_list member\'s topic FAILED!!!!!'
            print '@ ', each[1]
    cnx.close()
    return
    
def update_nogroup_art(uniqueID):
    #    Update the database
    #    Assign article as uniqueID to database as nogroup articles
    #    Nogroup articles with 0 similarity and FFFFF...  in topicID
    cnx =  mysql.connector.connect(user = DBuser, password = DBpass,
                                 host = DBhost,
                                 database='NewsDatabase')
    print "update_nogroup_art->Database connection successful!"
    newsDBcursor = cnx.cursor()
    checkQuery = ("""UPDATE originalArt SET topicID='FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF' WHERE uniqueID = %s;""")
    dataQuery = (uniqueID,)
    newsDBcursor.execute(checkQuery, dataQuery)
    cnx.commit()
#     print "update_nogroup_art-> Update originalArt successful!"
    
    checkQuery = ("""UPDATE summarizedArt SET topicID='FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF', similarity = 0 WHERE uniqueID = %s;""")
    dataQuery = (uniqueID,)
    newsDBcursor.execute(checkQuery, dataQuery)
    cnx.commit()
#     print "update_nogroup_art-> Update summarizedArt successful!"
    
#     selectData = newsDBcursor.fetchall()
    cnx.close()

def update_group_new_art(art_list):
    #    Update the database base on art_list
    #    Preprocess for update_group_art()
    #    Data structure of art_list
    #    [[topicID,uniqueID,SimilarityValue]]
    #    Attention!!!!!!:
    #    Only one article in art_list AND the article in art_list is a list in a list
    
    update_art_list = []
    groupArt = get_topic_art(art_list[0])
    value_arr = []
#     value_arr.append(art_list[2])
    this_art = get_art_DB(art_list[1])
    
    for each in groupArt:
        cur_art = get_art_DB(each[0])
        cur_value = each[4]
        w1 = this_art[6] + this_art[3] + this_art[4] 
        w2 = cur_art[6] + cur_art[3] + cur_art[4] 
        sim_value = keywordsComparator.cal_similarity(w1, w2)
        value_arr.append(sim_value)
        if cur_value > sim_value:
            cur_art_key = [cur_art[0],this_art[0],sim_value]
            update_art_list.append(cur_art_key)
        else:
            cur_art_key = [cur_art[0],this_art[0],cur_value]
            update_art_list.append(cur_art_key)
    
    value_arr.append(art_list[2])
    max_value = max(value_arr)
    cur_art_key = [art_list[0],this_art[0],max_value]
    update_art_list.append(cur_art_key)
    update_group_art(update_art_list)
    return

def compare_two_art(id1,id2):
    first_art = get_art_DB(id1)
    second_art = get_art_DB(id2)
    w1 = first_art[6] + first_art[3] + first_art[4]
    w2 = second_art[6] + second_art[3] + second_art[4]
    location1 = first_art[6]
    location2 = second_art[6]
    
    if not keywordsComparator.fast_compare(w1, w2, location1,location2):
        print 'compare_two_art-> '
        return 0
    if  first_art[0] == second_art[0]:
        print 'compare_two_art-> Same uniqueID, no need to compare' 
        print 'compare_two_art-> End of function'
        return 0
    if keywordsComparator.title_similarity(first_art[1], second_art[1], first_art[3], second_art[3]) and (first_art[0] != second_art[0]):
        print 'compare_two_art-> The articles with similar title, same!!!>>>>>>>>>>>>>>>>'
        print 'The title is ', first_art[1], ' and ', second_art[1]
        print 'compare_two_art-> End of function'
        return 5000
    a = keywordsComparator.cal_similarity(w1, w2)
    print 'compare_two_art-> The compare score is: ', a
    print '@ ', w1
    print '@ ', w2
    
    print 'compare_two_art-> End of function'
    return a


def compare_art_group(uniqueID, topicID):
    this_art = get_art_DB(uniqueID)
    topic_art_list = get_topic_art(topicID) #From summarizedArt, not real article
    
    if not topic_art_list:
        print 'compare_art_group-> There is no such topicID: ', topicID
        print 'compare_art_group-> End of function'
        return 
    art_count = 0
    value_a = []
    for each in topic_art_list:
        this_topic_art = get_art_DB(each[0])
        w1 = this_art[6] + this_art[3] + this_art[4]
        w2 = this_topic_art[6] + this_topic_art[3] + this_topic_art[4]
        location1 = this_art[6]
        location2 = this_topic_art[6]
        if this_art[0] == this_topic_art[0]:
            print 'compare_art_group-> Same uniqueID, continue to other articles'
            continue
        if keywordsComparator.title_similarity(this_art[1], this_topic_art[1], this_art[3], this_topic_art[3]) and (this_art[0] != this_topic_art[0]):
            print 'compare_art_group-> The articles with similar title, same!!!>>>>>>>>>>>>>>>>'
            print 'The title is ', this_art[1], ' and ', this_topic_art[1]
#             print 'compare_two_art-> End of function'
            art_count += 1
            value_a.append(5000)
            continue
        a = keywordsComparator.cal_similarity(w1, w2)
        value_a.append(a)
        print 'compare_art_group-> The compare score is: ', a, ' @ article ', art_count
        print '@ ', w1
        print '@ ', w2
        art_count += 1
    
    
    max_value = 0.0
    min_value = 9999.0 
    similar_title = 0
    for each in value_a:
        if each == 5000:
            similar_title += 1
            continue
        if max_value < each:
            max_value = each
        if min_value > each:
            min_value = each
    
    print 'compare_art_group-> The following is the result:'
    print 'The number of articles with similar title is: ', similar_title
    print 'The max value is: ', max_value
    print 'The min value is: ', min_value
    print value_a
    
    check_art_group_sim(uniqueID, topicID)
    
    print 'compare_art_group-> End of function'
    return


def remove_topic(topicID):
    
    cnx =  mysql.connector.connect(user = DBuser, password = DBpass,
                                 host = DBhost,
                                 database='NewsDatabase')
    print "refresh_topic_table->Database connection successful!"
    newsDBcursor = cnx.cursor()
    checkQuery = ("""UPDATE summarizedArt SET topicID='FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF',similarity = 0 WHERE topicID = %s""")
    try:
        newsDBcursor.execute(checkQuery, (topicID,))
        cnx.commit()
        print 'remove_topic-> Update summarizedArt successful~ @ ', topicID
    except mysql.connector.Error as e:
            print("Something went wrong: {}".format(e))
            print 'remove_topic -> Update summarizedArt for ',topicID,' FAILED!!!!!'
    
    #    The following codes are used to update originalArt table
    newsDBcursor = cnx.cursor()
    checkQuery = ("""UPDATE originalArt SET topicID='FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF' WHERE topicID = %s""")
    try:
        newsDBcursor.execute(checkQuery, (topicID,))
        cnx.commit()
        print 'remove_topic-> Update originalArt successful~ @ ', topicID
    except mysql.connector.Error as e:
            print("Something went wrong: {}".format(e))
            print 'remove_topic -> Update originalArt for ',topicID,' FAILED!!!!!'
    
    
    #    The following codes are used to delete topic row from topic table
    newsDBcursor = cnx.cursor()
    checkQuery = ("""DELETE FROM topic WHERE topicID = %s;""")
    try:
        newsDBcursor.execute(checkQuery, (topicID,))
        cnx.commit()
        print 'remove_topic-> Delete topic from topic successful~ @ ', topicID
    except mysql.connector.Error as e:
            print("Something went wrong: {}".format(e))
            print 'remove_topic -> Update topic for ',topicID,' FAILED!!!!!'
    
    return True


def refresh_topic_table():
    cnx =  mysql.connector.connect(user = DBuser, password = DBpass,
                                 host = DBhost,
                                 database='NewsDatabase')
    print "refresh_topic_table->Database connection successful!"
    newsDBcursor = cnx.cursor()
    checkQuery = ("""SELECT * FROM summarizedArt WHERE (topicID!='FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF');""")
    newsDBcursor.execute(checkQuery)
    summarizedArt = newsDBcursor.fetchall()
    #    Check if no articles at all
    if not summarizedArt:
        print "refresh_topic_table-> No articles in Database"
#         return
    else:    
    # Topic data is list, [[topicID, num_of_articles],[topicID, num_of_articles],..]
        topic_data = []
        for each in summarizedArt:
            cur_topicID = each[3]
            found_enrty = False
            for each_topic in topic_data:
                if each_topic[0] == cur_topicID:
                    each_topic[1] += 1
                    found_enrty = True
                    break
            if not found_enrty:
                newlist = [cur_topicID, 1]
                topic_data.append(newlist)
 
        
#         # First entry to topic_data
#         if not topic_data:
#             newlist = [cur_topicID, 1]
#             topic_data.append(newlist)
#             continue
#         # Check whether this id exits, if yes
#         for sub_list in topic_data:
#             if cur_topicID == sub_list[0]:
#                 sub_list[1] += 1
#                 continue
#             else:
#                 newlist = [cur_topicID, 1]
#                 topic_data.append(newlist)
    
        print 'refresh_topic_table-> Do database update'
        print topic_data
        for each in topic_data:
            #    Check if there is junk entry
            if each[1]<=1:
                remove_topic(each[0])
                continue
            else:
                topic_name = get_topic_name(each[0])
                checkQuery = ("""SELECT * FROM topic WHERE topicID = %s;""")
                newsDBcursor.execute(checkQuery,(each[0],))
                selectData = newsDBcursor.fetchone()
                if not selectData:  #    There is no this topicID, insert one
                    checkQuery = ("""INSERT INTO NewsDatabase.topic """
                                  """(topicID, name, numArt, score, entryDate, updateDate) """
                            """VALUES (%s,      %s,   %s,     %s,    CURDATE(),  CURDATE());""")
    #                 date = datetime.date.today()
                    dataQuery = (each[0],topic_name, each[1],0)
                    try:
                        newsDBcursor.execute(checkQuery,dataQuery)
                        cnx.commit()
                    except mysql.connector.Error as e:
                        print("Something went wrong: {}".format(e))
                        print "refresh_topic_table-> Insert new topic entry FAILED!!!! @ ", each[0],' @ ', topic_name
                        
                else:   #    Current topic entry exists, update it as well
                    checkQuery = ("""UPDATE topic SET name = %s, numArt = %s WHERE topicID = %s;""")
                    dataQuery = (topic_name, each[1])
                    try:
                        newsDBcursor.execute(checkQuery,dataQuery)
                        cnx.commit()
                    except mysql.connector.Error as e:
                        print("Something went wrong: {}".format(e))
                        print "refresh_topic_table-> Update old topic entry FAILED!!!! @ ", each[0],' @ ', topic_name
    print 'refresh_topic_table-> Finish 1st step of update, process eliminating junk entry'
    
    checkQuery = ("""SELECT * FROM topic;""")
    newsDBcursor.execute(checkQuery)
    topicData = newsDBcursor.fetchall()
    
    if not topicData:
        print 'refresh_topic_table-> No data in topic table'
#         return
    else:
        for each in topicData:
            topic_art_list = get_topic_art(each[0])
            if not topic_art_list:
                print 'refresh_topic_table-> No article in this topic: ', each[0]
                print 'Deleting this topic entry from topic table'
                remove_topic(each[0])
    print 'refresh_topic_table-> Finish deleting junk entry from topic table'
    return

def get_topic_name(topicID):
    topic_name = ''
    #    Temporary topic name for topicID holder 's title
    topic_art = get_art_DB(topicID)
    print 'get_topic_name-> The following is the list: topic_art'
    print topic_art
    topic_name = topic_art[1]
    return topic_name


def group_DB_check():
    #    Checking data consistency
    #    Get all articles
    all_article_list = get_all_art()
    
    for each in all_article_list:
        summarized_art = get_art_summarizedArt(each[0])
        if each[10] != summarized_art[3]:
            print 'group_DB_check-> Ori and Sum topicID different! Need repair'
            cnx =  mysql.connector.connect(user = DBuser, password = DBpass,
                                 host = DBhost,
                                 database='NewsDatabase')
            print "group_DB_check-> Database connection successful!"
            newsDBcursor = cnx.cursor()
            checkQuery = ("""UPDATE summarizedArt SET topicID= %s WHERE uniqueID = %s""")
            try:
                newsDBcursor.execute(checkQuery, (each[10],each[0]))
                cnx.commit()
                print 'group_DB_check-> Update summarizedArt successful~ uniqueID @ ', each[0]
            except mysql.connector.Error as e:
                    print("Something went wrong: {}".format(e))
                    print 'group_DB_check -> Update summarizedArt for ',each[0],' FAILED!!!!!'
        
    
    print 'group_DB_check-> Finish checking all attributes are correct.'
    return True

def group_art_new():
    #    The function to group all new articles, resort them into exist topic if available
    #    One time program, all article are sorted after this process
    ungroupArt = get_ungroup_art(force_group = True)
    if len(ungroupArt)==0:
        print 'group_art_new->No new news articles found!'
        return
    ID_list = []
    for each in ungroupArt:
        ID_list.append(each[0])
    otherArt = get_other_art(ID_list)
    groupArt = get_group_art()
    
    # Check grouped articles for similarity
    while len(ungroupArt)!=0:
        
        for each1 in ungroupArt:
            art_list = []
#             print each1
            w1 = each1[6] + each1[3] + each1[4]
            cur_max_value = 0.0
            # Check grouped articles for grouping
            num_remain_group_art = len(groupArt)
            for each2 in groupArt:
#                 art_list[:] = []
                cur_art = []
                if keywordsComparator.title_similarity(each1[1], each2[1], each1[3], each2[3]):
    #                 print 'The articles with similar title, same!!!>>>>>>>>>>>>>>>>'
    #                 print 'The title is ', each1[1], ' and ', each2[1]
#                     print 'group_art_new-> Inside title_similarity'
                    cur_art = [each2[0],each1[0],5000]
                    art_list[:] = []
                    art_list.append(cur_art)
                    break
                w2 = each2[6] + each2[3] + each2[4]
                location1 = each1[6]
                location2 = each2[6]
                if not keywordsComparator.fast_compare(w1, w2, location1, location2):
                    continue
#                 print 'group_art_new-> Before cal_similarity'
#                 print 'group_art_new-> w1 is : ', w1
#                 print 'group_art_new-> w2 is : ', w2 ,' @ ', each2[0]
                a = keywordsComparator.cal_similarity(w1, w2)
                ######################################################################################################
                if a >= similarity_value_rough:
                    print 'group_art_new-> Found topic possible for this article: ', each1[0], ' @ ', each2[0]
                    print 'with topicID; ', each2[10]
                    print 'The weighted score is: ', a, "for ", w1
                    print " and ", w2
                    cur_art = [each2[10],each1[0],a]
                    if check_art_group_sim(each1[0],each2[10]):
                        cur_max_value = a
                        art_list[:] = []
                        art_list.append(cur_art)
                        print 'group_art_new-> This article IS in this topic indeed! '
                        print 'group_art_new-> art_list is '
                        print art_list
                        break
                    print 'group_art_new-> This article is NOT in this topic indeed! After checking with other articles!'
                else:
                    print 'group_art_new-> Not a topic for this article: ', each1[0], ' @ article ', each2[0]
                    print 'The weighted score is: ', a, "for ", w1
                    print " and ", w2
                ######################################################################################################
                print 'group_art_new-> Checking grouped articles, there are ',num_remain_group_art,' grouped articles remaining~'
                num_remain_group_art-=1
            # If group similar article found, do this, then remove from ungroupArt, continue
            if len(art_list)!=0:
                print 'group_art_new-> updating new group article with following list:'
                print art_list
                update_group_new_art(art_list[0])
                ungroupArt.pop(0)
                groupArt = get_group_art()
                break
            else:
                ungroupArt.pop(0)
             
            
            # Still no similar art, nogroup
#             if len(art_list)==0:
#                 update_nogroup_art(each1[0])
#                 ungroupArt.pop(0)
#                 break
        print 'group_art_new-> Check grouped articles, there are ',len(ungroupArt),' remaining~'
        # While loop end from here, iteration is needed
    
    # Try to find group in all ungrouped articles
    ungroupArt = get_ungroup_art(force_group = False)
    print 'group_art_new-> After checked with grouped articles, there are ',len(ungroupArt),' remaining~'
    while len(ungroupArt)!= 0: 
        groupArtList = find_sim_art(ungroupArt)
        recal_sim_group(groupArtList)
        
        ungroupArt = get_ungroup_art(force_group = False)
        print 'group_art_new-> Checked with UNgrouped : ',len(ungroupArt),' remaining~'
    
    print 'group_art_new-> All new articles are grouped, end of group_art_new'
    print 'group_art_new-> Processing group_DB_ultimate_check now...'
    
    group_DB_ultimate_check()
    
    return
 
def check_art_group_sim(uniqueID, topicID):
    
    topic_art_list = get_topic_art(topicID)
    this_art = get_art_DB(uniqueID)
    
    if not topic_art_list:
        print 'check_art_group_sim-> No such topic!'
        return False
    print 'check_art_group_sim-> Start'
    sim_arr = []
    print 
    print topic_art_list
    print 
    for each in topic_art_list:
        cur_topic_art = get_art_DB(each[0])
        w1 = cur_topic_art[6] + cur_topic_art[3] + cur_topic_art[4]
        w2 = this_art[6] + this_art[3] + this_art[4]
        
        if cur_topic_art[0] == this_art[0]:
            continue
        
        if keywordsComparator.title_similarity(cur_topic_art[1], this_art[1], cur_topic_art[3], this_art[3]):
            sim_arr.append(similarity_value_precise)
            continue
        a = keywordsComparator.cal_similarity(w1, w2)
        sim_arr.append(a)
    
    avg_sim = sum(sim_arr)/ (float(len(sim_arr)))
    if avg_sim >= similarity_value_precise:
        print 'check_art_group_sim-> This article IS this group! @ value: ', avg_sim
        return True
    print 'check_art_group_sim-> This article is NOT this group @ value: ', avg_sim
    return False

def group_DB_ultimate_check():
    group_DB_check()
    refresh_topic_table()
    return

def group_art_all():
    #    The function to group all articles, clean database to group, very long time
    #    Normally use to group for a whole new database
    ungroupArt = get_ungroup_art(force_group = False)
    while len(ungroupArt)!= 0: 
        groupArtList = find_sim_art(ungroupArt)
        recal_sim_group(groupArtList)
        
        ungroupArt = get_ungroup_art(force_group = False)
    return
    

# Test main function


if __name__ == '__main__':
    
    group_art_new()
    
    print ("end of function")


