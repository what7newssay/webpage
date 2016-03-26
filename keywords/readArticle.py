from __future__ import with_statement
import mysql.connector
import io
import json
import os
from pyasn1.compat.octets import null
from __builtin__ import str
import re
from sqlalchemy import func
import uuid
import keywordsExtractor


class NewsReader:
	# Global status for analyze 
	totalNewsRead = 0;
	# The following variable will limit the current year to a certain year's news
	yearLimit = 2014;

def dataString(str):
	tempStr ='"'
	tempStr +=str
	tempStr +='"'
	return tempStr

def dbconnect():
# 	try:
		cnx =  mysql.connector.connect(user='WebAdmin', password='helloworld7',
                                 host='127.0.0.1',
                                 database='NewsDatabase')
 		print "Database connection successful!"
		return cnx
# 	except mysql.connector.Error as err:
#   		if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
#   			print("Something is wrong with your user name or password")
# 	 	elif err.errno == errorcode.ER_BAD_DB_ERROR:
# 	 		print("Database does not exist")
#   	else:
#   		print(err)
		
	
def updateDB(data, path):
	newsDB = dbconnect()
	newsDBcursor = newsDB.cursor()
	uniqueID = data['unique_id']
	print uniqueID
	checkQuery = ("""SELECT uniqueID FROM originalArt WHERE uniqueID = %s;""")
	newsDBcursor.execute(checkQuery, (uniqueID,))
	selectData = newsDBcursor.fetchall()
# 	numCount = len(selectData)
# 	print numCount
	if selectData:
# 	for row in selectData:
		print "Skip update>>>>>>>>>>>>>>>>>>>>This article already uploaded to database"
		return True
	# The codes below is for updating new article
	# Extract data from .json object
	publishDate = data['publish_date']['__value__']
	
	title = data['title'] 
	keywordsTitleData = keywordsExtractor.extract_title(title)
	keywords_title = ""
	for each in keywordsTitleData:
		keywords_title+= each
		keywords_title+= ","
	
	keywordsTextData = keywordsExtractor.extractKeyphrases(data['text'])
	keywordsComplexData = (keywordsTitleData + keywordsExtractor.ifin(keywordsTextData,keywordsTitleData))
	keywordsComplex = ""
	for each in keywordsExtractor.makeSingleString(keywordsComplexData):
		keywordsComplex+= each
		keywordsComplex+=","
	keywordsRaw = ""
	for each in data['keywords']:
		keywordsRaw += each
		keywordsRaw += ","
	for each in data['meta_keywords']:
		keywordsRaw += each
		keywordsRaw +=","
	geolocation = ""
	for each in data['location']:
		geolocation += each
		geolocation += ","
	path = path
	print keywords_title
	print keywordsComplex
	image_top = data['top_image']
# 	for each in data['top_image']:
# 		image_top += each
# 		image_top +=","
	images = ""
	for each in data['images']:
		images += each
		images +=","
		
# 	biID = func.UNHEX(uniqueID)
# 	uniqueID = func.UNHEX(uniqueID)
# 	print title
# 	print keywords
# 	print geolocation
# 	print path
	# Update Original Articles Database
	newsDBcursor = newsDB.cursor()
	
	add_article = ("""INSERT INTO NewsDatabase.originalArt """
					"""(uniqueID, title, path, keywords_title, keywords_complex, publish_date, geolocation, image_top, images, keywordsRaw) """
				"""VALUES (%s,     %s,    %s,    %s,             %s,             %s,          %s,        %s,        %s,           %s);""")
	data_article = (uniqueID, title, path, keywords_title,keywordsComplex, publishDate, geolocation, image_top, images, keywordsRaw)
# 	add_article = ("INSERT INTO originalArt "
#                "(uniqueID, title, path, keywords, upload_date, geolocation) "
#                "VALUES (%s, %s, %s, %s, %s, %s)")
# 	unhexString = "'(UNHEX('", uniqueID,"'))"
# 	data_article = (unhexString, title, path, keywords, "DATE()", geolocation)
 	
 	newsDBcursor.execute(add_article, data_article)
	print "Update Original Articles DB!"
	newsDB.commit()
	
	# The following codes will update summarized articles DB
	content = data['summary']
	
	
	add_article_sum = ("""INSERT INTO NewsDatabase.summarizedArt """
					"""(uniqueID, title, content) """
				"""VALUES (%s,     %s,    %s);""")
	data_article_sum = (uniqueID, title, content)
	newsDBcursor.execute(add_article_sum, data_article_sum)
	print "Update Summarized Articles DB!"
	newsDB.commit()
	
	
	newsDB.close()
	return True

def readJson(filepath):
	print "Processing the .json ", filepath
	
	with open(filepath) as obj:
		json_data = json.load(obj)
		if updateDB(json_data, filepath):
			NewsReader.totalNewsRead+=1
			json_data['DB_update'] = True
		obj.seek(0)
# 		obj.write(json.dumps(json_data))
# 		obj.truncate()
	

def read_news_files():
	folder_path_to_read = '/home/zhengzhenggao/ServerWeb/articles/original'

	for year in os.listdir(folder_path_to_read):
		if int(year) < NewsReader.yearLimit:
			continue
		firstLevelPath = os.path.join(folder_path_to_read, year)
# 			print firstLevelPath
		if os.path.isdir(firstLevelPath):
			for month in os.listdir(firstLevelPath):
				secondLevelPath = os.path.join(firstLevelPath, month)
# 					print secondLevelPath
				if os.path.isdir(secondLevelPath):
					for day in os.listdir(secondLevelPath):
						thirdLevelPath = os.path.join(secondLevelPath, day)
						for obj in os.listdir(thirdLevelPath):
							forthLevelPath = os.path.join(thirdLevelPath, obj)
							if obj.endswith(".json"):
								readJson(forthLevelPath)
								print "A .json object, filename is ", obj, " at ", day, " in ", month," IN ", year
							else:
								print "Not a .json object.... skip, the file name is ", obj, " at ", day," in ", month," IN ", year
			else:
					print "Second level : Unidentified file detected!"
					continue
		else:
			print "Top level : Unidentified file error!"
			continue			


def printStatus():
	print "The total number of news read is ", NewsReader.totalNewsRead	
	
if __name__ == '__main__':
    #test()
#	main()
    read_news_files()
    printStatus()
    print ("end of function")
	
	
