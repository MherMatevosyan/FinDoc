import sys, glob, os
sys.path.append(r'C:\Data_scraping\Financial_documents_research')
from findoc.currencies_regex import curr_regex # currency regex
from calendar import month_name
from nltk import ngrams
import re

class BaseVariable:

	"""Base variable class for hardcoded solution

	   attrs:
		 main_regex (str): main regex for a class
		 main_distance (int): main distance in words for a class
		 main_search_direction (str): the direction to search for the value
									  ('left','right','both')
		 keyword_dict (dict): keyword attributes dictionary, contains distance, search direction, regex
	"""

	def __init__(self):
		self.main_regex = ''
		self.main_distance = 0
		self.main_search_direction = 'both'
		self.keyword_dict = {}

	def min_dist_solution(self, words, keyword_dict = None):

		"""Finds minimal distance hardcoded solution.

		   args:
		     words (list): list of word tokens of pdf document
		     keyword_dict (dict): settings of keywords

		   return:
		   	 found word, position of found word, keyword with which word was found
		"""

		# default settings
		if keyword_dict == None:
			keyword_dict = self.keyword_dict

		indexed_text = list(enumerate(words))
		# all found keyword positions
		keyword_pos = []
		kw_counts = [(len(kw.split()),kw) for kw in keyword_dict]
		kw_length_set = set((l[0] for l in kw_counts))
		
		# seperate keywords by their length
		for length in kw_length_set:
			kw_lgram = ngrams(indexed_text, length)
			# start, end, ngram token
			kw_lgram_text = [(g[0][0],g[-1][0],' '.join([token[1] for token in g])) 
							 for g in kw_lgram]
			fixed_length_kw = [kw[1] for kw in kw_counts if kw[0] == length]
			
			fixed_keyword_pos = [(kw_s,kw_e,token) for kw_s,kw_e,token in kw_lgram_text
			 					 if token in fixed_length_kw]
			keyword_pos += fixed_keyword_pos
		# all found distances
		distances = []
		for kw_s,kw_e,kw in keyword_pos:
			distance = keyword_dict[kw]['distance']
			# TODO handle case when value we search for is consisted of multiple words
			regex_pattern = keyword_dict[kw]['regex']
			search_direction = keyword_dict[kw]['search_direction']
			# start of the block
			start = kw_s - distance if kw_s-distance > 0 else 0
			# end of the block
			end = kw_e + distance
			if search_direction == 'right':
				searchable_block = indexed_text[kw_e:end]
			elif search_direction == 'left':
				searchable_block = indexed_text[start:kw_s]
			elif search_direction == 'both':
				searchable_block = indexed_text[start:end]
			else:
				# mb hanlde search_direction value
				searchable_block = []
			
			value_pos = [index for index,value in searchable_block
						 if re.search(regex_pattern,value)]
			distance = [(self.dist(vp,kw_s,kw_e),vp,kw) for vp in value_pos]

			distances += distance
		if len(distances) == 0:
			return ('not found', None,'no kw')
		else:
			min_distance,found_target_pos,kw = min(distances)
			return words[found_target_pos],found_target_pos,kw

	@staticmethod
	def dist(vp,ks,ke):

		"""Small function to handle distance for min_dist_solution.

		   args:
		     vp (int): value position
		     ks (int): keyword start position
		     ke (int): keyword end position

		   return:
		     distance of value and keyword
		"""
		if vp > ke:
			return vp-ke
		elif vp < ks:
			return ks-vp
		else:
			#TODO mb raise error
			print("value and keyword cant be same!")

#############################################################################
### DATE CLASSES
#############################################################################

class DateVariable(BaseVariable):

	"""Class for variables with Date type

	   Dates are usually right from the keyword
	   and the preproccesing converts them to fit
	   '\\d{4}-\\d{2}-\\d{2}' regex
	"""

	def __init__(self):
		self.main_regex = '\\d{4}-\\d{2}-\\d{2}'
		self.main_distance = 10
		self.main_search_direction = 'right'
		self.keyword_dict = {}		

class MaturityDate(DateVariable):

	def __init__(self):
		super().__init__()
		self.name = 'maturity_date'
		self.keyword_dict = {'maturity':{'distance': self.main_distance, # nltk case: matur
										 'regex': self.main_regex,
										 'search_direction': self.main_search_direction},
							 'maturity date':{'distance': self.main_distance,
										 	  'regex': self.main_regex,
											  'search_direction': self.main_search_direction},
							 'due':{'distance': self.main_distance,
									'regex': self.main_regex,
									'search_direction': self.main_search_direction}
							}

class IssueDate(DateVariable):

	def __init__(self):
		super().__init__()
		self.name = 'issue_date'
		self.keyword_dict = {'issue':{'distance': self.main_distance, # nltk case: issu
									  'regex': self.main_regex,
									  'search_direction': self.main_search_direction}
							}

class FirstPaymentDate(DateVariable):

	def __init__(self):
		super().__init__()
		self.name = 'first_payment_date'
		self.main_distance = 25
		self.keyword_dict = {'payment':{'distance': self.main_distance,
										'regex': self.main_regex,
										'search_direction': self.main_search_direction}
						}	

	def find_day_and_month(self,first_payment_date):

		"""Find day and month of the first payment date

		   args:
			 first_payment_date (str): First Payment Date found form hardcoded solution

		   return:
			 tuple of day and month
		"""

		if first_payment_date != 'not found':
			payment_month = first_payment_date[-5:-3]
			payment_day = first_payment_date[-2:]
			return int(payment_day),month_name[int(payment_month)]
		else:
			return ('not found','not found')

	def find_frequency(self,first_payment_block):

		"""Find frequency of payments

		   args:
		     first_payment_block (str): text around first payment date

		   return:
		   	 frequency (annually, semi-annually, quarterly, monthly)
		"""

		annual_regex = "per annum|each year|yearly|annually|once a year|every year"
		annual = re.search(annual_regex,first_payment_block)
		if annual != None:
			annual = annual.group()
		semi_annual_regex = "semi-annually|semi annually"
		semi_annual = re.search(semi_annual_regex,first_payment_block)
		if semi_annual != None:
			semi_annual = semi_annual.group()
		quarter_regex = "quarterly"
		quarter = re.search(quarter_regex,first_payment_block)
		if quarter != None:
			quarter = quarter.group()
		month_regex = "per month|each month|monthly|once a month|every month"
		month = re.search(month_regex,first_payment_block)
		if month != None:
			month = month.group()
		return (annual,semi_annual,quarter,month)


#############################################################################
### NUMERIC CLASSES
#############################################################################		

class NumericVariable(BaseVariable):

	"""Class for variable with numeric or amount type

	   Amounts are usually big numbers seperated with commas
	   which to fit to '(?:^|\D)(\d{1,3}(?:,\d{3})+)(?:\D|$)' regex
	"""

	def __init__(self):
		self.main_regex = '(?:^|\D)(\d{1,3}(?:,\d{3})+)(?:\D|$)'
		self.main_distance = 10
		self.main_search_direction = 'both'
		self.keyword_dict = {}	

class IssueAmount(NumericVariable):

	def __init__(self):
		super().__init__()
		self.name = 'issue_amount'
		self.keyword_dict = {'Issue':{'distance': self.main_distance,
									  'regex': self.main_regex,
									  'search_direction': self.main_search_direction},
							 'issue':{'distance': self.main_distance,
									  'regex': self.main_regex,
									  'search_direction': self.main_search_direction},
							 'Nominal Aggregate Amount':{'distance': self.main_distance,
									   					 'regex': self.main_regex,
									   					 'search_direction': self.main_search_direction},
							 'Aggregate Principal Amount':{'distance': self.main_distance,
									   					   'regex': self.main_regex,
									   					   'search_direction': self.main_search_direction}
							}

#############################################################################
### PERCENTAGE CLASSES
#############################################################################		

class PercentVariable(BaseVariable):

	"""Class for variable with percentage type	   
	"""

	def __init__(self):
		self.main_regex = '^\d+\.\d+$|\d%'
		self.main_distance = 20
		self.main_search_direction = 'both'
		self.keyword_dict = {}	

class Coupon(PercentVariable):

	def __init__(self):
		super().__init__()
		self.name = 'coupon'
		# TODO should be customized enough to not make wrong outputs
		# TODO Needs to be divided in 3 categories
		# Fixed Rate, Floating Rate, Structured Notes, Zero Coupon, Fixed to Floating
		### Interest Basis or PROVISIONS RELATING TO INTEREST or INTEREST PROVISIONS or INTEREST
		### in these 2 usually all information about interest rate is contained
		self.keyword_dict = {'fixed':{'distance': self.main_distance,
									  'regex': self.main_regex,
									  'search_direction': self.main_search_direction},
							 'Fixed':{'distance': self.main_distance,
									  'regex': self.main_regex,
									  'search_direction': self.main_search_direction},
							 'Coupon':{'distance': self.main_distance,
									   'regex': self.main_regex,
									   'search_direction': self.main_search_direction},
							 'coupon':{'distance': self.main_distance,
									   'regex': self.main_regex,
									   'search_direction': self.main_search_direction},
							 'Interest':{'distance': self.main_distance,
										 'regex': self.main_regex,
										 'search_direction': self.main_search_direction},
							 'interest':{'distance': self.main_distance,
										 'regex': self.main_regex,
										 'search_direction': self.main_search_direction}
							}	
							 # 'floating':{'distance': self.main_distance,
								# 		 'regex': self.main_regex,
								# 		 'search_direction': self.main_search_direction},
							 # 'Floating':{'distance': self.main_distance,
								# 		 'regex': self.main_regex,
								# 		 'search_direction': self.main_search_direction},

	def find_note_type(self,words):

		"""Function which findes out Note type

		   types (Fixed Rate, Floating Rate,
		   		  Fixed to Floating Rate, Zero Coupon,
		   		  Structured Note)
		   args:
		     words (list): tokens in which type of Note should be found

		   return:

		"""
		rates = []
		fixed_rate = {'Fixed Rate':{'distance': 5,
									'regex': 'Applicable',
									'search_direction': 'right'}
					 }
		fr, fr_pos, fr_kw = self.min_dist_solution(words,fixed_rate)
		if fr_pos == None:
			rates.append(None)
		elif words[fr_pos-1] == 'Not':
			rates.append('not_fixed')
		else:
			rates.append('fixed')
		floating_rate = {'Floating Rate':{'distance': 5,
									      'regex': 'Applicable',
									      'search_direction': 'right'}
					    }
		flr, flr_pos, flr_kw = self.min_dist_solution(words,floating_rate)
		if flr_pos == None:
			rates.append(None)
		elif words[flr_pos-1] == 'Not':
			rates.append('not_floating')
		else:
			rates.append('floating')
		fixed_to_floating = {'Fixed to Floating':{'distance': 5,
									     		  'regex': 'Applicable',
									     		  'search_direction': 'right'}
							}
		ftflr, ftflr_pos, ftflr_kw = self.min_dist_solution(words,fixed_to_floating)
		if ftflr_pos == None:
			rates.append(None)
		elif words[ftflr_pos-1] == 'Not':
			rates.append('not_fixed_to_floating')
		else:
			rates.append('fixed_to_floating')
		zero_coupon = {'Zero Coupon':{'distance': 5,
									  'regex': 'Applicable',
									  'search_direction': 'right'}

					  }
		zc, zc_pos, zc_kw = self.min_dist_solution(words,zero_coupon)
		if zc_pos == None:
			rates.append(None)
		elif words[zc_pos-1] == 'Not':
			rates.append('not_zero_coupon')
		else:
			rates.append('zero_coupon')
		# Find 'Structured' tokens not following 'Hybrid' token
		struc_indexes = [i for i,w in enumerate(words) if w == 'Structured' and words[i-1] != 'Hybrid']
		struc_words = []
		# Extract 10 tokens after each 'Structured' token
		for i in struc_indexes:
			struc_words += words[i:i+10]
		structured_note = {'Structured':{'distance': 5,
									     'regex': 'Applicable',
									     'search_direction': 'right'},
						  }
		sn, sn_pos, sn_kw = self.min_dist_solution(struc_words,structured_note)
		if sn_pos == None:
			rates.append(None)
		elif words[sn_pos-1] == 'Not':
			rates.append('not_structured')
		else:
			rates.append('structured')

		return rates


class IssuePrice(PercentVariable):

	def __init__(self):
		super().__init__()
		self.name = 'issue_price'
		self.main_regex = '^\d+\.\d+$|\d%|^100$'
		# Issue Price is a percentage of IssueAmount(Nominal Aggregate Amount)
		keyword_dict = {'Issue Price':{'distance': 10,
									   'regex': self.main_regex,
									   'search_direction': 'right'}
									  }

#############################################################################
### TEXT CLASSES
#############################################################################	

class TextVariable(BaseVariable):

	"""Class for variable with text type

	   Here are Currencies, Issuers, frequency of payment etc.
	"""

	def __init__(self):
		# TODO yet needs to be changed to either '' or something that represents majority
		# of textual variables
		self.main_regex = '(?:|[^a-zA-Z])('+curr_regex+')(?:$|[^a-zA-Z])'
		self.main_distance = 20
		self.main_search_direction = 'right'
		self.keyword_dict = {}	

class Currency(TextVariable):

	def __init__(self):
		super().__init__()
		self.name = 'currency'
		self.main_regex = '(?:|[^a-zA-Z])('+curr_regex+')(?:$|[^a-zA-Z])'
		self.keyword_dict = {'currency':{'distance': self.main_distance,
										 'regex': self.main_regex,
										 'search_direction': self.main_search_direction},
							 'Currency':{'distance': self.main_distance,
										 'regex': self.main_regex,
										 'search_direction': self.main_search_direction}
							}

	def find_currency_from_issue_amount(self,issue_amount):

		"""Checks if there is currency from curr_regex in issue amount

		   args:
			 issue_amount (str): Issue Amount found form hardcoded solution

		   return (str):
			 returns found abbrevation
		"""

		curr_from_ia = re.search(curr_regex,issue_amount)
		try:
			return curr_from_ia.group()			
		except AttributeError:
			pass