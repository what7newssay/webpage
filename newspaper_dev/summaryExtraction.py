__author__ = 'Chun-kit YEUNG'

#from __future__ import absolute_import
#from __future__ import division, print_function, unicode_literals

from sumy.summarizers.luhn import LuhnSummarizer
from sumy.summarizers.edmundson import EdmundsonSummarizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.summarizers.text_rank import TextRankSummarizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.summarizers.sum_basic import SumBasicSummarizer
from sumy.summarizers.kl import KLSummarizer

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

LANGUAGE = 'english'
SENTENCES_COUNT = 5

AVAILABLE_METHODS = {
	'luhn': LuhnSummarizer,
	'edmundson': EdmundsonSummarizer,
	'lsa': LsaSummarizer,
	'text-rank': TextRankSummarizer,
	'lex-rank': LexRankSummarizer,
	'sum-basic': SumBasicSummarizer,
	'kl': KLSummarizer,
}

METHODS_LIST = [ 
	'luhn',
	'edmundson',
	'lsa',
	'text-rank',
	'lex-rank',
	'sum-basic',
	'kl',
]

def get_summary(summarize_method = 'lsa', string = '', 
	language = LANGUAGE, num_of_sentences = SENTENCES_COUNT):
	#parse string
	parser = PlaintextParser.from_string(string, Tokenizer(language))

	#stop word
	stop_words = get_stop_words(language)

	#building summarizer
	summarizer_class = AVAILABLE_METHODS[summarize_method]
	stemmer = Stemmer(language)
	summarizer = summarizer_class(stemmer)
	
	#set parameter to summarizer
	if summarizer_class is EdmundsonSummarizer:
		summarizer.null_words = stop_words
		summarizer.bonus_words = parser.significant_words
		summarizer.stigma_words = parser.stigma_words
	else:
		summarizer.stop_words = stop_words

	#get summary
	summary = summarizer(parser.document, num_of_sentences)

	return summary

	
def test():
	for method in METHODS_LIST:
		input_str = 'Malaysia raised its security alert level after an attack in Jakarta, Indonesia in January\n\nMalaysian authorities say 15 people suspected of planning attacks on the country have been arrested.\n\nAll are suspected of links to the so-called Islamic State (IS) militant group said the national police chief.\n\nThe 15, including one police officer, were arrested over three days in the capital, Kuala Lumpur, and six other states, said Khalid Abu Bakar.\n\nOne hundred and seventy-seven suspected militants have been detained in Malaysia in the past three years.\n\nThe authorities said the suspects were trying to obtain chemicals to make bombs and were planning to launch attacks. They were aged between 22 to 49 and included four women who were planning to travel to Syria to join IS, they said.\n\nThe police chief said the group also arranged for two foreign terror suspects to sneak out of Malaysia, and had channelled money to militants in the southern Philippines.\n\nMalaysia is on a particularly high terror alert since the capital of neighbouring Jakarta was attacked by militants in January.\n\nOn 15 January, Malaysian police said they had arrested a man they claimed was hours from carrying out a suicide attack in Kuala Lumpur.'
		summary = get_summary(method, input_str, LANGUAGE, 5)
		print ('summary_method:', method)
		for t in summary:
			print (t)
		print ()


if __name__ == '__main__':
	test()