import mysql.connector
import serverConfiguration
import time


################################################################################
#    Variable section
#    The following is the database variable
DBuser =  serverConfiguration.DBuser
DBpass = serverConfiguration.DBpass
DBhost = serverConfiguration.DBhost
################################################################################

def dbconnect():
    #    Database connection initializer
    cnx =  mysql.connector.connect(user = DBuser, password = DBpass,
                             host = DBhost,
                             database='NewsDatabase')
    print "Database connection successful!"
    return cnx

###############################################################################
#    Geo loaction database loader
def load_city_file():
    print 'load_city_file-> Loading city location'
    file = open('./geo_data/worldcitiespop.txt','r')
    line_count = 0
    line_total = 3173959
    start_time = time.time()
    for line in file:
        if line.startswith('#'):
            line_count += 1
            continue
        data_list = line.split(',')
        update_database_city(data_list)
        line_count += 1
        cur_time_diff = time.time() - start_time
        rate = line_count/cur_time_diff
        seconds = (line_total - line_count) / rate % 60
        minutes = (line_total - line_count) / rate // 60
        print 'There are ', line_total - line_count, ' lines left, at speed ', rate, ' lines per second'
        print 'Approximately ', minutes, 'Mins ', seconds, 'Secs left to finish.'
    
    print 'load_city_file-> Finish updating city list'
    return

def update_database_city(data_list):
    #    Update city database
    country_code = data_list[0].upper()
    city_name = data_list[1].title()
    
    latitude = data_list[5]
    longitude = data_list[6]
    location_str = latitude + ',' + longitude
    cnx = dbconnect()
    newsDBcursor = cnx.cursor()
    checkQuery = ("""SELECT * FROM locationCountry WHERE country_code = %s;""")
    dataQuery = (country_code,)
    newsDBcursor.execute(checkQuery, dataQuery)
    selectData = newsDBcursor.fetchone()
    
    if not selectData:
        print 'update_database_city-> (Extract) No such country find, skip this city'
        return
    
    country_num = selectData[0]
    country_name = selectData[1]
    
    #    Debug use
    print 'This city name: ', city_name
    
    newsDBcursor = cnx.cursor()
    checkQuery = ("""SELECT * FROM locationCity WHERE city_name = %s;""")
    dataQuery = (city_name,)
    try:
        newsDBcursor.execute(checkQuery, dataQuery)
        selectData = newsDBcursor.fetchone()
    except mysql.connector.Error:
        print 'There is error when checking this city_name'
        print 'This city name: ', city_name
        print 'Skip this city to process'
        return
    if selectData:
        print 'update_database_city-> (Update) Already in database, skip this city'
        return
    
    
    print country_num,' ',country_code,' ',country_name, ' ', city_name, ' ',location_str
    
    newsDBcursor = cnx.cursor()
    checkQuery = ("""INSERT INTO locationCity (country_num, country_code, country_name, city_name, location) VALUES """
                                            """(%s,         %s,            %s,            %s,           %s);""")
    dataQuery = (country_num, country_code, country_name, city_name, location_str)
    try:
        newsDBcursor.execute(checkQuery, dataQuery)
        cnx.commit()
    except mysql.connector.Error:
        print 'update_database_city-> (Update) Updating this city failed @ ', city_name, ' country_name ', country_name
        print
        return
    print 'update_database_city-> (Last) Finished updating this city'
    return

def load_country_file():
    print 'load_country_file-> (First) Loading cow.txt, country list file'
    file = open('./geo_data/cow.txt','r')
    
    for line in file:
        if line.startswith('#'):
            continue
        data_list = line.split('; ')
        print data_list
#         update_database_country_1(data_list)
    file.close()
    print 'load_country_file-> Finished cow.txt, processing next file'
    
    file = open('./geo_data/country_latlon.csv')
    
    for line in file:
        if line.startswith('#'):
            continue
        data_list = line.split(',')
        print data_list
        update_database_country_2(data_list)
    file.close()

    
    print 'load_country_file-> Finished country_latlon.csv'
    return

def update_database_country_2(data_list):
    #    Update database from country name file
    country_code = data_list[0]
    latitude = data_list[1]
    longitude = data_list[2]
    location_str = latitude + ',' + longitude
    
    cnx = dbconnect()
    newsDBcursor = cnx.cursor()
    checkQuery = ("""UPDATE locationCountry SET location = %s WHERE country_code = %s """)
    dataQuery = (location_str, country_code)
    newsDBcursor.execute(checkQuery, dataQuery)
    cnx.commit()
    print 'update_database_country_2-> Finishing updating country_latlon.csv into database'
    return

def update_database_country_1(data_list):
    #    Update database from country latlon file
    country_code = data_list[0]
    country_num = data_list[2]
    country_name = data_list[4]
    
    
    cnx = dbconnect()
    newsDBcursor = cnx.cursor()
    checkQuery = ("""INSERT INTO locationCountry (country_code, country_num, country_name) VALUES """
                                                """(%s,            %s,        %s);""")
    dataQuery = (country_code, country_num, country_name)
    newsDBcursor.execute(checkQuery, dataQuery)
    cnx.commit()
    print 'update_database_country_1-> Finishing updating cow.txt into database'
    return


###############################################################################
#    Ranking calculation section


###############################################################################
###############################################################################

if __name__ == '__main__':
#     load_country_file()
#     load_city_file()
    print 'End of function'