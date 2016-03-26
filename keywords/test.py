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

cnx =  mysql.connector.connect(user='WebAdmin', password='helloworld7',
                                 host='127.0.0.1',
                                 database='NewsDatabase')
print "Database connection successful!"
newsDBcursor = cnx.cursor()
checkQuery = ("""SELECT * FROM originalArt WHERE topicID = '"UNDEFINE"';""")
newsDBcursor.execute(checkQuery)
selectData = newsDBcursor.fetchall()
selecData_to = list(selectData)
selecData_to.pop(0)
art_list = []
total_num_art = len(selectData)*len(selectData)
for each1 in selectData:
    w1 = each1[3] + each1[4]
    for each2 in selecData_to:
        if keywordsComparator.title_similarity(each1[3], each2[3]):
            total_num_art -= 1
            print 'The articles with similar title, same!!!>>>>>>>>>>>>>>>>'
            print 'The title is ', each1[1], ' and ', each2[1]
            continue
        w2 = each2[3] + each2[4]
        a = keywordsComparator.cal_similarity(w1, w2)
        if a >=500:
            print 'The weighted score is: ', a, "for ", w1
            print " and ", w2
        if (total_num_art % 200 ==0):
            print "Remaining artiles ", total_num_art
        total_num_art -= 1
        
    break
cnx.close()

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

