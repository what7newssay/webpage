from nltk.corpus import wordnet as wn
from nltk.corpus import wordnet_ic
brown_ic = wordnet_ic.ic('ic-brown.dat')
semcor_ic = wordnet_ic.ic('ic-semcor.dat')
from nltk.corpus import genesis
genesis_ic = wn.ic(genesis, False, 0.0)
import keywordsComparator
import mysql.connector
import copy


# for word1 in list1:
#     for word2 in list2:
#         wordFromList1 = wordnet.synsets(word1)
#         wordFromList2 = wordnet.synsets(word2)
#         if wordFromList1 and wordFromList2: #Thanks to @alexis' note
#             for each1 in wordFromList1:
#                 for each2 in wordFromList2:
#                     s = each1.wup_similarity(each2)
#                     list.append(s)
# 
# print(max(list))
# hit = wn.synsets('hit', pos=wn.VERB)
# slap = wn.synsets('hit', pos=wn.VERB)
# 
# for each1 in hit:
#     for each2 in slap:
#         s = each1.lch_similarity(each2)
#         list.append(s)
# hit = wn.synsets('hit', pos=wn.NOUN)
# slap = wn.synsets('slap', pos=wn.NOUN)
# for each1 in hit:
#     for each2 in slap:
#         s = each1.lch_similarity(each2)
#         list.append(s)
# print (max(list))

# dog.lin_similarity(cat, semcor_ic)

# hit = wn.synsets('cat', pos=wn.VERB)
# slap = wn.synsets('kitten', pos=wn.VERB)
# 
# for each1 in hit:
#     for each2 in slap:
#         s = each1.lin_similarity(each2, semcor_ic)
#         list.append(s)

def get_group_art():
    cnx =  mysql.connector.connect(user='WebAdmin', password='helloworld7',
                                 host='127.0.0.1',
                                 database='NewsDatabase')
    print "get_art_DB->Database connection successful!"
    newsDBcursor = cnx.cursor()
    checkQuery = ("""SELECT * FROM originalArt WHERE (topicID != '"UNDEFINE"' AND topicID != 'FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF');""")
    newsDBcursor.execute(checkQuery)
    selectData = newsDBcursor.fetchall()
    cnx.close()
    return selectData

def get_topic_art(topicID):
    cnx =  mysql.connector.connect(user='WebAdmin', password='helloworld7',
                                 host='127.0.0.1',
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
    cnx =  mysql.connector.connect(user='WebAdmin', password='helloworld7',
                                 host='127.0.0.1',
                                 database='NewsDatabase')
    print "get_art_DB->Database connection successful!"
    newsDBcursor = cnx.cursor()
    checkQuery = ("""SELECT * FROM originalArt WHERE uniqueID = %s;""")
    newsDBcursor.execute(checkQuery, (uniqueID,))
    selectData = newsDBcursor.fetchone()
    cnx.close()
    return selectData

def get_other_art(art_list):
    get_list =[]
    cnx =  mysql.connector.connect(user='WebAdmin', password='helloworld7',
                                 host='127.0.0.1',
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
    cnx =  mysql.connector.connect(user='WebAdmin', password='helloworld7',
                                 host='127.0.0.1',
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
    
    ID_list = []
    ID_list.append(art_list[0])
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
            
               
    
    return art_list


def remove_art_from_list(artID,artList):
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
    result_list = art_list
    print result_list
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
    cnx =  mysql.connector.connect(user='WebAdmin', password='helloworld7',
                                 host='127.0.0.1',
                                 database='NewsDatabase')
    print "update_group_art->Database connection successful!"
    newsDBcursor = cnx.cursor()
    
 
    checkQuery = ("""UPDATE summarizedArt SET topicID= %s, similarity = %s, updateDate = NOW() WHERE uniqueID = %s;""")
    dataQuery = (art_list[0][0],art_list[0][2],art_list[0][0])
    try:
        newsDBcursor.execute(checkQuery, dataQuery)
        cnx.commit()
        print 'update_group_art-> Update summarizedArt successful! @ ', art_list[0][0]
        
    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err))
        print 'update_group_art -> Update summarizedArt for main topic holder FAILED!!!!!'
    
    checkQuery = ("""UPDATE originalArt SET topicID= %s WHERE uniqueID = %s;""")
    dataQuery = (art_list[0][0],art_list[0][0])
    try:
        newsDBcursor.execute(checkQuery, dataQuery)
        cnx.commit()
        print 'update_group_art-> Update originalArt successful! @ ', art_list[0][0]
    except mysql.connector.Error as e:
        print 'update_group_art -> Update originalArt for main topic holder FAILED!!!!!'
    
    
    newsDBcursor = cnx.cursor()
    for each in art_list:
        if each[2] <0:
            continue
        checkQuery = ("""UPDATE summarizedArt SET topicID= %s, similarity = %s, updateDate = NOW() WHERE uniqueID = %s;""")
        dataQuery = (each[0],each[2],each[1])
        try:
            newsDBcursor.execute(checkQuery, dataQuery)
            cnx.commit()
            print 'update_group_art-> Update summarizedArt successful! @ ', each[1]
        except mysql.connector.Error as e:
            print("Something went wrong: {}".format(e))
            print 'update_group_art -> Update summarizedArt for art_list member topic holder FAILED!!!!!'
            print '@ ', each[1]
        
        checkQuery = ("""UPDATE originalArt SET topicID= %s WHERE uniqueID = %s;""")
        dataQuery = (each[0],each[1])
        try:
            newsDBcursor.execute(checkQuery, dataQuery)
            cnx.commit()
            print 'update_group_art-> Update originalArt successful! @ ', each[1]
        except mysql.connector.Error as e:
            print("Something went wrong: {}".format(e))
            print 'update_group_art -> Update originalArt for art_list member topic holder FAILED!!!!!'
            print '@ ', each[1]
    cnx.close()
    return
    
    
def update_nogroup_art(uniqueID):
    cnx =  mysql.connector.connect(user='WebAdmin', password='helloworld7',
                                 host='127.0.0.1',
                                 database='NewsDatabase')
#     print "update_nogroup_art->Database connection successful!"
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
    update_art_list = []
    groupArt = get_topic_art(art_list[0])
    value_arr = []
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
            

# The function to group all new articles, resort them into exist topic if availiable
def group_art_new():
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
            
            # Check grouped articles for grouping
            for each2 in groupArt:
                cur_art = []
                if keywordsComparator.title_similarity(each1[3], each2[3]):
    #                 print 'The articles with similar title, same!!!>>>>>>>>>>>>>>>>'
    #                 print 'The title is ', each1[1], ' and ', each2[1]
#                     print 'group_art_new-> Inside title_similarity'
                    cur_art = [each2[0],each1[0],5000]
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
                    art_list.append(cur_art)
                    break
                ######################################################################################################
            
            # If group similar article found, do this, then remove from ungroupArt, continue
            if len(art_list)!=0:
                print 'group_art_new-> before update_group_new_art, the art_list is ',art_list
                update_group_new_art(art_list[0])
                ungroupArt.pop(0)
                groupArt = get_group_art()
                break
            
            
            # Still no similar art, nogroup
            if len(art_list)==0:
                update_nogroup_art(each1[0])
                ungroupArt.pop(0)
                break

        # While loop end from here, iteration is needed
    # Try to find group in all ungrouped articles
    ungroupArt = ungroupArt = get_ungroup_art(force_group = False)
    while len(ungroupArt)!= 0: 
        groupArtList = find_sim_art(ungroupArt)
        recal_sim_group(groupArtList)
        
        ungroupArt = get_ungroup_art(force_group = False)
        
    return
    
    

# The function to group all articles, clean database to group, very long time   
def group_art_all():
    ungroupArt = get_ungroup_art(force_group = False)
    while len(ungroupArt)!= 0: 
        groupArtList = find_sim_art(ungroupArt)
        recal_sim_group(groupArtList)
        
        ungroupArt = get_ungroup_art(force_group = False)
    return
    

# Test main function
if __name__ == '__main__':
    
    group_art_new()
    
#     ungroupArt = get_ungroup_art(force_group = True)
#     groupArtList = find_sim_art(ungroupArt)
#     print groupArtList
#     recal_sim_group(groupArtList)
#     ungroupArt = get_ungroup_art(force_group = False)
#     while len(ungroupArt)!= 0:
#         
#         groupArtList = find_sim_art(ungroupArt)
#         recal_sim_group(groupArtList)
#         
#         ungroupArt = get_ungroup_art(force_group = False)
#         
#     
#     
    print ("end of function")



# Similar example
# w1 = "Bottega,Veneta,Fall,Milan,Fashion,Week,diary,Coverage,Russ,McClintock,"
# w2 = "Milan,Fashion,Week,Dsquared2,Fall,diary,Coverage,Russ,McClintock,"
# 
# w1 = "amazing,sports,photos,29,Paris,terror,attacks,college,football,game,Hide,Caption,moment,Marcell,Mercedes,Sophie,Tempe,Doha,Bernier,Lewis,Malcolm,timeout,volleyball,Giginoglu,perform,points,truck,Jenkins,Alexis,SMU,Reynolds,Maple,Smith,cornerback,McKeehen,title,pass,rebound,Gathers,England,Washington,touchdown,Grand,Maryland,Iowa,Prix,Holm,Hamilton,linebacker,Baylor,basketball,Zach,Tuesday,light,Robertson,win,Ateman,teammate,fight,York,Philadelphia,City,Qatar,Annapolis,Thursday,player,Utah,Louis,Zealand,receiver,driver,St,Park,Rousey,race,victory,Arizona,NFL,yards,Navy,career,season,tournament,NHL,quarterback,State,event,Kentucky,record,Saturday,New,Friday,Sunday,Hide,November,Caption,shot,"
# w2 = "amazing,sports,photos,37,San,Jose,State,college,basketball,game,Hide,Caption,wide,receiver,Suarez,driver,Hawaii,Kentucky,Dante,Mikael,leaps,Mirco,playoff,class,South,Alec,Houston,Major,Whitfield,Alexander,Mexico,Hertha,MX,Pogba,Wasps,Emirates,races,teeth,Chen,Roger,Sprint,Reynolds,Marathon,Mississippi,defenders,go,defender,title,Connecticut,pass,Dubai,Toluca,Dural,New,York,Washington,Radionova,team,Busch,play,Chepstow,Red,Carolina,Prix,Berlin,McIlroy,Adelaide,Kansas,win,Los,Alvarez,Ohio,shoots,California,forward,Memphis,tournament,Detroit,competition,Beamer,player,record,Grand,face,Virginia,field,Angeles,end,center,Philadelphia,compete,United,Tour,pounds,event,Florida,Tuesday,receiver,Cup,Dallas,kilograms,season,Michigan,Columbus,football,home,Friday,World,Thursday,goal,NHL,match,Sunday,Saturday,Hide,Caption,shot,November,"
# Not similar example
# w1 = "farm,breeds,bullfrogs,Singapore,farm,breeds,adults-only,elixir,Royal,Hashima,Dessert,Jurong,Frog,Farm,Traditional,Chinese,Medicine,American,bullfrogs,Jackson,Wan,life,cycle,data,tradition,refreshing,Ginseng,age,counter,disease,kilogram,supermarkets,concrete,paradigm,tubes,trade,texture,level,affect,stage,benefits,contains,number,size,system,lungs,populations,figure,protein,species,puberty,hormones,fruit,blood,egg,skin,children,health,meat,year,life,recommend,cycle,don,time,Jackson,Bickford,drink,Wan,be,American,hashima,"
# w2 = "public,housing,Luxury,hotel,Singapore-style,things,make,amount,parts,Provident,Minister,projects,pension,buildings,practice,blocks,plans,director,CNN,hawker,Kampung,squatter,center,light,changer,resale,profit,costs,mass,Yew,Northshore,Trust,gardens,surge,centers,window,bedrooms,get,put,climate,buzz,residents,open,lot,construction,developments,include,room,project,Development,communal,development,models,Skyville,plan,Residents,building,rule,apartments,years,Hassell,government,HDB,flats,"

# a = keywordsComparator.cal_similarity(w1, w2)
# print ('The weighted score is: ', a)

