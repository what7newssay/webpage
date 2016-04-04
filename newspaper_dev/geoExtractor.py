__author__ = 'Chun-kit YEUNG'

import nltk
from newspaper import Article
from nltk.tag import StanfordNERTagger
from collections import Counter
import csv
import re
from geopy.geocoders import Nominatim

#load the geolocator
geolocator = Nominatim()

#load the dictionary
country_adj_to_noun_dict = {}

with open('./geo_data/cow.csv', 'r') as f:
	reader = csv.DictReader(f)
	for row in reader:
		adj = row['BGN_demomyn_adj']
		noun = row['ISOen_proper']
		country_adj_to_noun_dict[adj] = noun



class Extractor(object):
	def __init__(self, text=None, url=None):
		if not text and not url:
			raise Exception ('text or url is needed')
		self.text = text
		self.url = url
		self.places = []
		if self.url is not None:
			pass

	def named_entities(self):
		text = nltk.word_tokenize(self.text)
		pos_tag = nltk.pos_tag(text)
		entities = nltk.chunk.ne_chunk(pos_tag)
		return entities
	
	def find_entities(self):
		GPE_list = []
		entities = self.named_entities()
		for ne in entities:
			if type(ne) is nltk.tree.Tree:
				#['GPE', 'PERSON', 'ORGANIZATION']
				if ne.label() in ['GPE']:
					GPE_list.append(u' '.join(i[0] for i in ne.leaves()))

		#convert country's adjective to noun
		for GPE in GPE_list:
			temp = GPE
			if temp in country_adj_to_noun_dict.keys():
				temp = country_adj_to_noun_dict[GPE]
			self.places.append(temp) 

		#only country is selected
		"""
		for GPE in GPE_list:
			temp = GPE
			if temp in country_adj_to_noun_dict.keys():
				temp = country_adj_to_noun_dict[GPE]
				self.places.append(temp)
			elif temp in country_adj_to_noun_dict.values():
				self.places.append(temp)
		"""
			
	
	def get_entities_with_count(self):
		entities_count = Counter()
		for ne in self.places:
			entities_count[ne] += 1 

		return entities_count

def get_locations_and_latlog(input_str, num_of_locations = 3):
	extractor = Extractor(text = input_str)
	extractor.find_entities()
	ranks = extractor.get_entities_with_count().most_common(num_of_locations)
	
	location_and_latlog_dict = {}

	for rank in ranks:
		loc = rank[0]
		location = geolocator.geocode(loc)
		if location:
			#print (loc)
			location_and_latlog_dict[loc] = '{0},{1}'.format(location.latitude, location.longitude)


	return location_and_latlog_dict

def get_locations(input_str, num_of_locations = 3):
	extractor = Extractor(text = input_str)
	extractor.find_entities()
	ranks = extractor.get_entities_with_count().most_common(num_of_locations)
	locations = []
	for rank in ranks:
		locations.append(rank[0])
	return locations

def get_locations_latlog(input_str = None, locs_list = None, num_of_locations = 3):
	if (input_str is None) & (locs_list is None):
		return []
	elif (input_str is not None) & (locs_list is None) :
		locs_list = get_locations(input_str = input_str, num_of_locations = num_of_locations)
	
	#if the list is empty 
	if not locs_list:
		return []

	lat_log_list = []
	for loc in locs_list:
		location = geolocator.geocode(loc)
		lot_log_str = '{0},{1}'.format(location.latitude, location.longitude)
		lat_log_list.append(lot_log_str)

	return lat_log_list


if __name__ == '__main__':
	t = "Ray is Washingtong"
	location = get_locations_and_latlog(t)
	print (location)

