__author__ = 'Chun-kit YEUNG'

import nltk
from newspaper import Article
from nltk.tag import StanfordNERTagger
from collections import Counter

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
		entities = self.named_entities()
		for ne in entities:
			if type(ne) is nltk.tree.Tree:
				#['GPE', 'PERSON', 'ORGANIZATION']
				if ne.label() in ['GPE']:
					self.places.append(u' '.join(i[0] for i in ne.leaves()))
	
	def get_entities_with_count(self):
		entities_count = Counter()
		for ne in self.places:
			entities_count[ne] += 1 

		return entities_count


def get_locations(input_str, num_of_locations = 3):
	extractor = Extractor(text = input_str)
	extractor.find_entities()
	ranks = extractor.get_entities_with_count().most_common(num_of_locations)
	locations = []
	for rank in ranks:
		locations.append(rank[0])
	return locations



if __name__ == '__main__':
	url = 'http://lens.blogs.nytimes.com/2016/02/19/robert-james-campbell-jessica-ferber-rebirth-of-the-cool/?module=BlogPost-Title&version=Blog Main&contentCollection=Multimedia&action=Click&pgtype=Blogs&region=Body'
	a = Article(url)
	a.download()
	a.parse()
	extractor = Extractor(text=a.text)
	extractor.find_entities()
	print (extractor.places)
