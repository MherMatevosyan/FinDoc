import nltk
import datetime

# -------------------------------------------------------------------
# NEEDS TO BE POPULATED WITH POSSIBLE DATE FORMATS.
all_formats = ["%d %b %Y","%d %B %Y"]

# -------------------------------------------------------------------
# SYNONYMS NEED TO BE FOUND
# Maturity date stemmed synonym list
mdate_list = ['matur','due'] # termination (not tested)

# -------------------------------------------------------------------
# GENERAL NOTES
# Text of pdfs must be preproccesed (remove \n, \x0c, stemming, etc.)
# Some functions use text version, others word tokenization of pdf


# -------------------------------------------------------------------
def find_target_value(words: list, target: str) -> list:
    """Function to find target value in a given text.
    
       words: word tokenized text of pdf (preproccesed)
       target: target value
       
       return: list of positions of the target values, if any was found.
    """
    
    list_of_target_positions = [count for count,word in enumerate(words) if word == target]
    if len(list_of_target_positions) != 0:
        return list_of_target_positions
    else:
        print('no target was found!')
        return 'no target was found!'

# -------------------------------------------------------------------
def find_mdate(text: str,
               date: str,
               desired_format = "%Y-%m-%d",
               date_formats = all_formats,
               return_positions = False) -> tuple:
    
    """Function to find Maturity Dates in text document and
       change those Maturity Dates to desired format.
    
       text: text version of pdf document
       date: Maturity date
       desired_format: Ideal format of date
       date_formats: list of all date formats
       return_positions: return also positions of mdates
       
       return: First element of the tuple is modified text with all
               maturity date formats changed to desired format. Second
               element is a list of positions of maturity dates.
               
    """
    
    for other_format in date_formats:
        date_object = datetime.datetime.strptime(date , desired_format).strftime(other_format)       
        text = text.replace(date_object,date)
    if return_positions:
        words = nltk.word_tokenize(text)
        return (text,find_target_value(words,date))
    else:
        return (text,[])

# -------------------------------------------------------------------
def find_keyword_block(words: list,
                       keywords: list,
                       word_threshold = 50,
                       concat = False) -> list:
    
    """Function to find the text blocks of keywords.
    
       words: word tokenized text of pdf (preproccesed)
       keyword: list of synonim keywords (all small case)
       word_threshold: how many words to spread around the keyword
       concat: combine all text blocks accounting for overlapping
       
       return: nested list of text blocks, keyword position and keyword.
    """
    
    
    block_positions = []
    for keyword in keywords:
        # Finding positions of keywords
        list_of_keyword_position = [count for count,word in enumerate(words) if keyword in word.lower()]
        for position in list_of_keyword_position:
            start = position-word_threshold if position-word_threshold>0 else 0
            end = position+word_threshold
            block_coordinates = [start,end,position,keyword]
            block_positions.append(block_coordinates)
    
    # Sorting text blocks by starting position
    sorted_positions = sorted(block_positions)  
    
    # Removing overlaps
    if concat:        
        pre = sorted_positions[:-1]
        post = sorted_positions[1:]
        for count, (pre_block, post_block) in enumerate(zip(pre,post)):
            if pre_block[1] >= post_block[0]:
                # Seperate text blocks by the mean of keyword positions
                border = (pre_block[2]+post_block[2])//2+1
                sorted_positions[count][1] = border
                sorted_positions[count+1][0] = border

    return [[' '.join(words[start:end]),pos,kw] for start,end,pos,kw in sorted_positions]

# -------------------------------------------------------------------
def find_keyword_position(keyword: str,
                          text_blocks: list) -> list:
    """Function to extract the positions of a given keyword
    
       keyword: given keyword
       text_blocks: text blocks, which is the output of find_keyword_block
       
       return: list of positions
    """
    
    return [block[1] for block in text_blocks if block[2] == keyword]
