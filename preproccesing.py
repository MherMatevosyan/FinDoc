import nltk
import datetime

# NEEDS TO BE POPULATED WITH POSSIBLE DATE FORMATS.
all_formats = ["%d %b %Y","%d %B %Y"]

# GENERAL NOTES
# Text of pdfs must be preproccesed (remove \n, \x0c, stemming, etc.)
# Some functions use text version, others word tokenization of pdf


# -------------------------------------------------------------------
def find_target_value(words: list, target: str) -> list:
    """Function to find target value in a given text.
    
       words: word tokenized text of pdf (preproccesed)
       target: target value
       
       return: list of positions of the target values, if any was found."""
    
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
       date_formats: all date formats
       return_positions: return also positions of mdates
       
       return: First element of the tuple is modified text with all
               maturity date formats changed to desired format. Second
               element is a list of positions of maturity dates.
               
    """
    
    for other_format in date_formats:
        date_object = datetime.datetime.strptime(date , desired_format).strftime(other_format)       
        text = text.replace(date_object,date)
    if return_positions:
        return (text,find_target_value(text,date))
    else:
        return (text,[])

# -------------------------------------------------------------------
def find_keyword_block(words: list,
                       keywords: list,
                       word_threshold = 50,
                       concat = False,
                       return_positions = False) -> list:
    
    """Function to find the text blocks of keywords.
    
       words: word tokenized text of pdf (preproccesed)
       keyword: list of synonim keywords (all small case)
       word_threshold: how many words to spread around the keyword
       concat: combine all text blocks accounting for overlapping
       return_postitions: return also positions of keywords
       
       return: list of text blocks where the keyword is.
               If return_positions is True returns nested lists, where
               first element is the blcok and second element is the position.
    """
    
    list_of_blocks = []
    for keyword in keywords:
        # Find positions of keywords
        list_of_keyword_position = [count for count,word in enumerate(words) if keyword in word.lower()]
        
        if concat:
            for count, position in enumerate(list_of_keyword_position):
                start = position-word_threshold if position-word_threshold > 0 else 0
                end = position+word_threshold
                if count == 0: #First text block
                    text_block = ' '.join(words[start:end])
                    if return_positions:
                        list_of_blocks.append([text_block,position])
                    else:
                        list_of_blocks.append(text_block)
                    overlap_pos = end
                else:
                    preoverlap_pos = start
                    if preoverlap_pos <= overlap_pos: # checking for overlap
                        text_block = ' '.join(words[overlap_pos:end])
                        if return_positions:
                            list_of_blocks.append([text_block,position])
                        else:
                            list_of_blocks.append(text_block)
                    else:
                        text_block = ' '.join(words[start:end])
                        if return_positions:
                            list_of_blocks.append([text_block,position])
                        else:
                            list_of_blocks.append(text_block)

                    overlap_pos = end
                    
        else: # ignoring overlap
            for position in list_of_keyword_position:
                start = position-word_threshold if position-word_threshold > 0 else 0
                end = position+word_threshold
                text_block = ' '.join(words[start:end])
                if return_positions:
                    list_of_blocks.append([text_block,position])
                else:
                    list_of_blocks.append(text_block)

               
    return list_of_blocks
