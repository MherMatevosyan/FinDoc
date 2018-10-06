import re
import nltk


def percentage_tokenizer(words: list)-> list:
    
    """Function to convert all percentages tokens to universal iiipercentiii token.
    
        words: Word tokenized text of pdf (preproccesed)
        
        return: Converted list of tokens
    """
    final_words = words[:]
    pattern = re.compile('\d+\.\d+')
    for c,word in enumerate(final_words):
        m = re.match(pattern,word)
        if m != None:
            final_words[c] = "iiiPERCENTiii"
    return final_words

def id_tokenizer(words: list) -> list:
    
    """Function to convert all id like tokens to universal iiiPERCENTiii token.
    
        words: Word tokenized text of pdf (preproccesed)
        
        return: Converted list of tokens
    """
    final_words = words[:]
    for c,word in enumerate(final_words):
        new_word = word.replace('-','')        
        if len(new_word) != len(word) and new_word.isdigit():
            final_words[c] = "iiiIDiii"
    return final_words

def integer_tokenizer(words: list) -> list:
    
    """Function to convert all integer like tokens to universal iiiINTiii token.
    
        words: Word tokenized text of pdf (preproccesed)
        
        return: Converted list of tokens
    """
    final_words = words[:]
    for c,word in enumerate(final_words):
        word = word.replace(',','')
        try:
            n = int(word)
            final_words[c] = 'iiiINTiii'
        except ValueError:
            pass
    return final_words

def date_postproccess_case(words: list) -> list:
    
    """Function to make iiidateiii to iiiDATEiii
    
       words: Word tokenized text of pdf (preproccesed)
        
       return: Converted list of tokens
    """
    return [w if w!='iiidateiii' else 'iiiDATEiii' for w in words]

def word_slash_divider(words: list) -> list:
    
    """Fuction that finds tokens that are consisted of 2 words seperated witha slash and divides them.
    
       words: Word tokenized text of pdf (preproccesed)
        
       return: Converted list of tokens    
    """
    
    final_words = words[:]
    stemmer = nltk.stem.PorterStemmer()
    pattern = re.compile('[a-z]+/[a-z]+')
    count = 0 
    for word in words:
        m = re.search(pattern,word)
        if m != None:
            splitted = word.split('/')
            stemmed = [stemmer.stem(w) for w in splitted]
            del final_words[count]
            final_words[count:count] = stemmed
            count+=1
        count+=1
    return final_words

def uni_token_normalizer(words: list) -> list:
    words = integer_tokenizer(words)
    words = id_tokenizer(words)
    words = percentage_tokenizer(words)
    words = date_postproccess_case(words)
    words = word_slash_divider(words)
    return(words)
