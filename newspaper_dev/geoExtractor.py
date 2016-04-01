__author__ = 'Chun-kit YEUNG'

import nltk
from newspaper import Article
from nltk.tag import StanfordNERTagger
from collections import Counter
import csv
import re
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


def get_locations(input_str, num_of_locations = 1):
	extractor = Extractor(text = input_str)
	extractor.find_entities()
	ranks = extractor.get_entities_with_count().most_common(num_of_locations)
	locations = []
	for rank in ranks:
		locations.append(rank[0])
	return locations



if __name__ == '__main__':
	t = "I Greece Greek Chinese Chinese Greek Chinese Greek Greece Chinese EU EU EU China"
	location = get_locations(t)
	print (location)

