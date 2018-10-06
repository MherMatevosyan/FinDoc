import sys, os, glob
sys.path.append(r'C:\Data_scraping\Financial_documents_research')
from findoc.currencies_regex import curr_regex 
import HardcodedVariableClassesV2 as HVC
import HardcodedPreproccessing as HP
import csv
import re
from tqdm import tqdm



# initialize variables
col_names = ['ISIN']
MDate = HVC.MaturityDate()
col_names.append(MDate.name)
IDate = HVC.IssueDate()
col_names.append(IDate.name)
FPDate = HVC.FirstPaymentDate()
col_names.append(FPDate.name)
IAmount = HVC.IssueAmount()
col_names.append(IAmount.name)
IPrice = HVC.IssuePrice()
col_names.append(IPrice.name)
Coupon = HVC.Coupon()
col_names.append(Coupon.name)
Currency = HVC.Currency()
col_names.append(Currency.name)
col_names += ['payment_month','payment_day']


# write columns
csv_file_name = 'harcoded_floating_test.csv'
with open(csv_file_name,'w') as csv_file:
	writer=csv.writer(csv_file, lineterminator = '\n')
	writer.writerow(col_names)

path = os.getcwd()+'\\'
files = [os.path.basename(file) for file in glob.glob(path+'/*.pdf')]

for file in tqdm(files):
	targets = []
	reader = HP.PDFReader(file)
	reader.read_pdf()
	targets.append(reader.pdf_name[:-4])
	preproccesor = HP.Preproccessing(reader.pdf_doc)
	preproccesor.general_preproccesing()
	if preproccesor.pdf_doc == '':
		# in case there was/were image in 1 or more page(s)
		continue
	else:				
		# preproccessing for date format variables
		# WARNING: using nltk_normalize slows down the algorithm and makes it worse
		date_words = preproccesor.date_preproccessing()
		# As indexing needs to be kept when finding other variables throigh maturity
		# date, then some cases need te preserve letter cases
		date_words_upper = preproccesor.date_preproccessing(lowercase = False)
		# preproccesing for other formats
		other_words = preproccesor.normal_preproccessing()

		##################################################################
		### MATURITY DATE
		##################################################################
		maturity_date, md_pos, md_kw = MDate.min_dist_solution(date_words)
		targets.append(maturity_date)

		##################################################################
		### ISSUE DATE
		##################################################################
		issue_date, id_pos, id_kw = IDate.min_dist_solution(date_words)
		targets.append(issue_date)

		##################################################################
		### FIRST PAYMENT DATE
		##################################################################
		### First payment date must be decided after we find out if the note is
		### fixed rate, floating rate or structered, as for each FPD may be found
		### in a different way
		first_payment_date, fpd_pos,fpd_kw = FPDate.min_dist_solution(date_words)
		targets.append(first_payment_date)
		# check if first payment is on maturity date, then there is only one payment
		if first_payment_date == maturity_date and maturity_date != 'not found':
			freq = 'one payment'
		elif fpd_pos != None:
			first_payment_block = date_words[max(fpd_pos-5,0):fpd_pos+FPDate.main_distance]
			first_payment_block_string = ' '.join(first_payment_block).lower()
			freq = FPDate.find_frequency(first_payment_block_string)
			
		else:
			freq = 'not found'
		#print(targets[0],freq)

		##################################################################
		### ISSUE AMOUNT
		##################################################################
		# Check if maturity date was found with 'due' keyword
		# then search issue amount before that maturity date
		# IMPORTANT: keep same preproccessing for 'due' case as token
		# indexes might change depending on different types of preproccessing
		# NOTE: mb just add due keyword with settings below, as maturity date
		# was not found in one case (that case is found by nominal aggregate amount).


		if md_kw == 'due':
			amd_start = max(md_pos - IAmount.main_distance,0)  # start of text block
			issue_amount, ia_pos, ia_kw = IAmount.min_dist_solution(date_words_upper[amd_start:md_pos], 
																	keyword_dict = {'due':{'distance': 20,
																						   'regex': IAmount.main_regex,
										 												   'search_direction': 'left'}
										 											})
			if issue_amount != 'not found':
				targets.append(issue_amount)
			else:
				issue_amount, ia_pos, ia_kw = IAmount.min_dist_solution(other_words)
				targets.append(issue_amount)				
		else:
			issue_amount, ia_pos, ia_kw = IAmount.min_dist_solution(other_words)
			targets.append(issue_amount)

		##################################################################
		### Issue Price
		##################################################################		
		issue_price, ip_pos, ip_kw = IPrice.min_dist_solution(other_words)
		# if issue amount was found while issue price was not, most
		# probably it is 100 % MIGHT NEED CHECK
		if issue_price == 'not found' and issue_amount != 'not found':
			issue_price = '100'
		targets.append(issue_price)

		##################################################################`
		### COUPON
		##################################################################
		coupon_types = Coupon.find_note_type(other_words)
		new_types = [c for c in coupon_types if c != None and 'not' not in c]
		if coupon_types[0] == 'fixed' and coupon_types[1] != 'floating':
			# Fixed interest rate
			coupon, co_pos, co_kw = Coupon.min_dist_solution(other_words)
			targets.append(coupon)
		elif coupon_types[0] != 'fixed' and coupon_types[1] == 'floating':
			# Floating interest rate
			# TODO: IBOR regex should be changed to more general, e.g. see list of all possible floating rates
			coupon, co_pos, co_kw = Coupon.min_dist_solution(other_words,
															 keyword_dict =  {'Reference Interest Rate':{'distance': 10,
																			   	 	 					 'regex': 'IBOR',
							 												  	 	 					 'search_direction': 'right'},
							 												  'Reference Rate':{'distance': 10,
																			   	 	 			'regex': 'IBOR',
							 												  	 	 			'search_direction': 'right'} 
							 									 			  })
			margin, m_pos, m_kw = Coupon.min_dist_solution(other_words,
														   keyword_dict =  {'Margin':{'distance': 10,
																			   	 	  'regex': Coupon.main_regex,
							 												  	 	  'search_direction': 'right'},
							 												'Margin(s)':{'distance': 10,
																			   	 	  	 'regex': Coupon.main_regex,
							 												  	 	  	 'search_direction': 'right'} 
							 									 			  })						
			search_block = ' '.join(other_words[co_pos-10:co_pos+1])
			float_rate_final = re.search(co_kw+'\s(.*?'+coupon+')',search_block).group(1)
			targets.append(float_rate_final+' + '+margin)
			print(float_rate_final,margin,targets[0])
		elif len(new_types) == 0:
			targets.append('not_found')
		else:
			targets.append(new_types)

		# ### Check sections in beetween 'INTEREST' tokens.
		# interest_poses = [index for index,w in enumerate(other_words) if w == 'INTEREST']
		# # If 'INTEREST' doesn't exists search in whole document
		# if len(interest_poses) == 0:
		# 	find_note_words = other_words
		# 	coupon_types = Coupon.find_note_type(find_note_words)
		# 	if coupon_types[0] == 'fixed' and coupon_types[1] != 'floating':
		# 		coupon, co_pos, co_kw = Coupon.min_dist_solution(find_note_words)
		# 		targets.append(coupon)
		# 	elif any(c is not None for c in coupon_types):
		# 		targets.append('not_found')
		# 	else:
		# 		targets.append([c for c in coupon_types if c != None and 'not' not in c])
		# # If only one 'INTEREST' exist search after it in 1000 tokens
		# elif len(interest_poses) == 1:
		# 	find_note_words = other_words[interest_poses[0]:interest_poses[0]+1000]
		# 	coupon_types = Coupon.find_note_type(find_note_words)
		# 	if coupon_types[0] == 'fixed' and coupon_types[1] != 'floating':
		# 		coupon, co_pos, co_kw = Coupon.min_dist_solution(find_note_words)
		# 		targets.append(coupon)
		# 	elif any(c is not None for c in coupon_types):
		# 		targets.append('not_found')
		# 	else:
		# 		targets.append([c for c in coupon_types if c != None and 'not' not in c])
		# else:
		# 	# Initialize list for all cases of 'INTEREST'
		# 	all_coupon_types = []
		# 	for i in range(len(interest_poses)-1):
		# 		start = interest_poses[i]
		# 		end = interest_poses[i+1]
		# 		find_note_words = other_words[start:end]
		# 		coupon_types = Coupon.find_note_type(find_note_words)
		# 		if any(c is not None for c in coupon_types):
		# 			all_coupon_types.append((coupon_types,find_note_words))
		# 	find_note_words = other_words[interest_poses[-1]:interest_poses[-1]+1000]
		# 	coupon_types = Coupon.find_note_type(find_note_words)
		# 	if any(c is not None for c in coupon_types):
		# 		all_coupon_types.append((coupon_types,find_note_words))
		# 	try:
		# 		main_coupon_type = max([(len([d for d in c if d!= None]),c,nw) for c,nw in all_coupon_types])
		# 	except ValueError:
		# 		targets.append('not_found')
		# 	else:
		# 		if main_coupon_type[1][0] == 'fixed' and main_coupon_type[1][1] != 'floating':
		# 			coupon, co_pos, co_kw = Coupon.min_dist_solution(main_coupon_type[2])
		# 			targets.append(coupon)
		# 		else:
		# 			targets.append([c for c in main_coupon_type[1] if c != None and 'not' not in c])


		##################################################################
		### CURRENCY
		##################################################################
		# 1. Check if issue amount was found, then check if it was found with 'due'
		# keyword and search for currency in text block around found issue amount
		# 2. Check from found issue amount if there is currency abbrevation
		# 3. Check from found issue amount if there is currency symbol
		# If found add first abbrevation, second symbol, thrid currency around
		# issue amount and last originally found currency
		currency, cu_pos,cu_kw = Currency.min_dist_solution(other_words)
		if ia_pos != None:
			aa_start = max(ia_pos - Currency.main_distance,0) # start of text block
			# check around found issue amount 
			if ia_kw == 'due':
				# handle case when issue amount was found using 'due'
				# using the same text block as in issue amount case
				aa_currency, aa_cu_pos, aa_cu_kw = Currency.min_dist_solution(date_words_upper[amd_start:md_pos],
																			  keyword_dict =  {'due':{'distance': 10,
																			   	 					  'regex': Currency.main_regex,
							 												  	 					  'search_direction': 'left'}
							 													  			  })
			else:
				aa_currency, aa_cu_pos, aa_cu_kw = Currency.min_dist_solution(other_words[aa_start:ia_pos],
																			  keyword_dict =  {'due':{'distance': Currency.main_distance,
																			   						  'regex': Currency.main_regex,
							 												  					 	  'search_direction': 'left'}
							 																  })
		else:
			aa_currency = None
		currency_from_ia = Currency.find_currency_from_issue_amount(issue_amount)
		if currency_from_ia != None:
			targets.append(currency_from_ia)
		elif aa_currency != 'not found' and aa_currency != None:
			# drop all extra non-letter characters
			targets.append(re.search(curr_regex,aa_currency).group())
		elif currency == 'not found':
			targets.append(currency)
		else:
			# drop all extra non-letter characters
			targets.append(re.search(curr_regex,currency).group())

		##################################################################
		### FIRST PAYMENT DAY AND MONTH
		##################################################################
		day, month = FPDate.find_day_and_month(first_payment_date)
		targets.append(month)
		targets.append(day)

		# append a row to csv file
		with open(csv_file_name,'a') as csv_file:

			writer = csv.writer(csv_file, lineterminator = '\n')
			try:
				writer.writerow(targets)
			except UnicodeDecodeError:
				print(file,'could not be written')
