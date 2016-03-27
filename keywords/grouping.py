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

#################################################################################
# Database variable
DBuser = 'WebAdmin'
DBpass = 'helloworld7'
DBhost = '127.0.0.1'
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
        w1 = each1[3] + each1[4]
        for index1,each2 in enumerate(selectData_to, start=index):
            cur_art = []
            if keywordsComparator.title_similarity(each1[3], each2[3]):
                total_num_art -= 1
#                 print 'The articles with similar title, same!!!>>>>>>>>>>>>>>>>'
#                 print 'The title is ', each1[1], ' and ', each2[1]
                cur_art = [each1[0],each2[0],5000]
                art_list.append(cur_art)
                continue
            w2 = each2[3] + each2[4]
            location1 = each1[6]
            location2 = each2[6]
            if not keywordsComparator.fast_compare(w1, w2, location1, location2):
                continue
            
            a = keywordsComparator.cal_similarity(w1, w2)
            ######################################################################################################
            if a >= 3:
                print 'The weighted score is: ', a, "for ", w1
                print " and ", w2
                cur_art = [each1[0],each2[0],a]
                art_list.append(cur_art)
            ######################################################################################################
            if (total_num_art % 20 ==0):
                print "Remaining articles ", total_num_art
            total_num_art -= 1
            index += 1
        if len(art_list)==0:
            update_nogroup_art(each1[0])
            if len(selectData) >= 2:
                selectData.pop(0)
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
    topicID = ID_list.pop(0)
    print
    print topicID
    print
    print otherArt_list
    for each1 in ID_list:
        this_art = get_art_DB(each1)
        for each2 in otherArt_list:
            cur_art = []
            w1 = this_art[3] + this_art[4]
            w2 = each2[3] + each2[4]
            location1 = this_art[6]
            location2 = each2[6]
            if not keywordsComparator.fast_compare(w1, w2, location1,location2):
                continue
            
            if keywordsComparator.title_similarity(this_art[3], each2[3]):
#               print 'The articles with similar title, same!!!>>>>>>>>>>>>>>>>'
#               print 'The title is ', each1[1], ' and ', each2[1]
                cur_art = [topicID,each2[0],5000]
                art_list.append(cur_art)
                otherArt_list = remove_art_from_list(each2[0],otherArt_list)
                continue
            a = keywordsComparator.cal_similarity(w1, w2)
            ######################################################################################################
            if a >= 3:
                print 'The weighted score is: ', a, "for ", w1
                print " and ", w2
                cur_art = [topicID,each2[0],a]
                art_list.append(cur_art)
                otherArt_list = remove_art_from_list(each2[0],otherArt_list)
            ######################################################################################################
            
               
    # Debug only
#     print '*************************************find_sim_art'
#     for each in art_list:
#         print '*************************************'
#         print   
#         print each
#         print
#         print
#     print '**************************************'
    
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
    result_list = art_list
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
    
    for each1 in process_list:
        value_arr = []
        ori_value = result_list[process_count][2]
        for each2 in process_list_to:
            if each1[0] == each2[0]:
                print 'Same uniqueID: ',each1[0],' and ',each2[0]
                continue
            if keywordsComparator.title_similarity(each1[3], each2[3]):
                print 'recal_sim_group->Same title detection'
                value_arr.append(5000)
                break
            w1 = each1[3] + each1[4]
            w2 = each2[3] + each2[4]
            a = keywordsComparator.cal_similarity(w1, w2)
            print 'Did calculation at ',each1[0],' and ',each2[0],' @ ',a
            value_arr.append(a)
        value_arr.append(result_list[process_count][2])
        print value_arr
        max_value = max(value_arr)
        
        ###################################################################################
        if ori_value == max_value and max_value<7:
            result_list[process_count][2] = -1
        else:
            result_list[process_count][2] = max_value
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
    value_arr.append(art_list[2])
    this_art = get_art_DB(art_list[1])
    
    for each in groupArt:
        cur_art = get_art_DB(each[0])
        cur_value = each[4]
        w1 = this_art[3] + this_art[4] 
        w2 = cur_art[3] + cur_art[4] 
        sim_value = keywordsComparator.cal_similarity(w1, w2)
        value_arr.append(sim_value)
        if cur_value > sim_value:
            cur_art_key = [cur_art[0],this_art[0],sim_value]
            update_art_list.append(cur_art_key)
        else:
            cur_art_key = [cur_art[0],this_art[0],cur_value]
            update_art_list.append(cur_art_key)
    max_value = max(value_arr)
    cur_art_key = [art_list[0],this_art[0],max_value]
    update_art_list.append(cur_art_key)
    update_group_art(update_art_list)
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
    
    newsDBcursor = cnx.cursor()
    checkQuery = ("""UPDATE originalArt SET topicID='FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF',similarity = 0 WHERE topicID = %s""")
    try:
        newsDBcursor.execute(checkQuery, (topicID,))
        cnx.commit()
        print 'remove_topic-> Update originalArt successful~ @ ', topicID
    except mysql.connector.Error as e:
            print("Something went wrong: {}".format(e))
            print 'remove_topic -> Update originalArt for ',topicID,' FAILED!!!!!'
    
    newsDBcursor = cnx.cursor()
    checkQuery = ("""DELETE FROM topic WHERE topicID = %s;""")
    try:
        newsDBcursor.execute(checkQuery, (topicID,))
        cnx.commit()
        print 'remove_topic-> Delete topic successful~ @ ', topicID
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
    checkQuery = ("""SELECT * FROM summarizedArt""")
    newsDBcursor.execute(checkQuery)
    summarizedArt = newsDBcursor.fetchall()
    #    Check if no articles at all
    if not summarizedArt:
        print "refresh_topic_table-> No articles in Database"
        return
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
        else:
            topic_name = get_topic_name(each[0])
            checkQuery = ("""SELECT * FROM topic WHERE topicID = %s""")
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
    return

def get_topic_name(topicID):
    topic_name = ''
    #    Temporary topic name for topicID holder 's title
    topic_art = get_art_DB(topicID)
    topic_name = topic_art[1]
    return topic_name


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
            w1 = each1[3] + each1[4]
            cur_max_value = 0.0
            # Check grouped articles for grouping
            num_remain_group_art = len(groupArt)
            for each2 in groupArt:
                cur_art = []
                if keywordsComparator.title_similarity(each1[3], each2[3]):
    #                 print 'The articles with similar title, same!!!>>>>>>>>>>>>>>>>'
    #                 print 'The title is ', each1[1], ' and ', each2[1]
#                     print 'group_art_new-> Inside title_similarity'
                    cur_art = [each2[0],each1[0],5000]
                    art_list[:] = []
                    art_list.append(cur_art)
                    break
                w2 = each2[3] + each2[4]
                location1 = each1[6]
                location2 = each2[6]
                if not keywordsComparator.fast_compare(w1, w2, location1, location2):
                    continue
#                 print 'group_art_new-> Before cal_similarity'
#                 print 'group_art_new-> w1 is : ', w1
#                 print 'group_art_new-> w2 is : ', w2 ,' @ ', each2[0]
                a = keywordsComparator.cal_similarity(w1, w2)
                ######################################################################################################
                if a >= 5:
                    print 'The weighted score is: ', a, "for ", w1
                    print " and ", w2
                    cur_art = [each2[0],each1[0],a]
                    if cur_max_value < a:
                        art_list[:] = []
                        art_list.append(cur_art)
                    
                    continue
                ######################################################################################################
                print 'group_art_new-> Checking grouped articles, there are ',num_remain_group_art,' grouped articles remaining~'
                num_remain_group_art-=1
            # If group similar article found, do this, then remove from ungroupArt, continue
            if len(art_list)!=0:
#                 print 'group_art_new-> before update_group_new_art, the art_list is ',art_list
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
    
#     group_art_new()
    refresh_topic_table()
    print ("end of function")


