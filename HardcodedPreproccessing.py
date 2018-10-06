import sys, glob, os
sys.path.append(r'C:\Data_scraping\Financial_documents_research')
from findoc.pdf2text import pdf2text
from findoc.find_image import find_image
from findoc.normalizer import nltk_normalize
import findoc.preproccesing as prep
import re


class PDFReader:

	"""Just reads pdf and converts it to text

	   args:
		 pdf_name (str): name of pdf document
	"""

	def __init__(self,pdf_name):
		self.pdf_name = pdf_name
		self.pdf_doc = ''

	def read_pdf(self):

		"""Converts pdf to text"""
		try:
			self.pdf_doc = pdf2text(self.pdf_name)
		except Exception  as e:
			#print(self.pdf_name,e)
			pass


class Preproccessing:

	"""CLass for different types of preproccesing

	   args:
		 pdf_doc: pdf document in string
	"""

	def __init__(self,pdf_doc):
		self.pdf_doc = pdf_doc


	def general_preproccesing(self):

		if find_image(self.pdf_doc) == 0:
			# remove new lines and new pages
			self.pdf_doc = self.pdf_doc.replace('\n',' ').replace('\x0c',' ')
			# change multiple whitespaces to 1 whitespace
			self.pdf_doc = re.sub(' +',' ',self.pdf_doc)
		else:
			# TODO mb make an error concerning to this
			#print('1 or more pages of PDF is/are image(s).')
			self.pdf_doc = ''

	def date_preproccessing(self, nltk_normalized = False, lowercase = True):

		"""Preproccess the document for date formats.

		   args:
			 nltk_normalize (bool): use nltk_normalize or split by whitespace
			 lowercase (bool): use lowercasing all letters
		"""

		# remove any punctuation followed by whitespace
		### In order to convert dates in text to datetime objects we need to get rid of punctuations
		### following words, so for e.g. "2017," will become "2017". It affects also words like
		### "Maturity:" & "Interest:" making them "Maturity" & "Interest".
		date_preproccessed = re.sub('([?,:;.!]+)(\s)',r'\2',self.pdf_doc)
		# remove 'th|nd|st|rd' if it is after digit
		### "10th", "2nd" and other such dates mess up datetime parser
		date_preproccessed = re.sub('(\d+)(th|nd|st|rd)(\s)',r'\1\3',date_preproccessed)
		# convert all dates to one format
		date_preproccessed = prep.date_converter_faster(date_preproccessed,prep.all_formats,span = 50) 
		if nltk_normalized: # lowercase doesn't have effect in this case
		
			tokenized_text = nltk_normalize(date_preproccessed)
		elif lowercase:
			tokenized_text = date_preproccessed.split(' ')
			tokenized_text = [t.lower() for t in tokenized_text if t != '']
		else:
			tokenized_text = date_preproccessed.split(' ')
			tokenized_text = [t for t in tokenized_text if t != '']			
		return tokenized_text 


	def digit_preproccessing(self):

		return [t.lower() for t in self.pdf_doc.split(' ') if t != '']

	def normal_preproccessing(self):

		#TODO: remove (s) from end of tokens mb for all cases of preproccesing

		preproccessed = re.sub('([?,:;.!]+)(\s)',r'\2',self.pdf_doc)
		return [t for t in preproccessed.split(' ') if t != '']

