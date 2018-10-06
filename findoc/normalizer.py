import re, string, unicodedata
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
import inflect


def remove_non_ascii(words):
    """Remove non-ASCII characters from list of tokenized words"""
    new_words = []
    for word in words:
        new_word = unicodedata.normalize('NFKD', word).encode('ascii', 'ignore').decode('utf-8', 'ignore')
        new_words.append(new_word)
    return new_words

def to_lowercase(words):
    """Convert all characters to lowercase from list of tokenized words"""
    return [w.lower() for w in words]

def remove_punctuation(words):
    """Remove punctuation from list of tokenized words"""
    new_words = []
    for word in words:
        new_word = re.sub(r'[^\w\s]', '', word)
        if new_word != '':
            new_words.append(new_word)
    return new_words

def remove_punctuation_whole(words):
    """Remove punctuation from list of tokenized words if token is only punctuation"""
    new_words = []
    for word in words:
        new_word = ''.join(re.findall(r'[^\w\s]', word))
        if new_word != word:
            new_words.append(word)
    return new_words

def replace_numbers(words):
    """Replace all interger occurrences in list of tokenized words with textual representation"""
    p = inflect.engine()
    new_words = []
    for word in words:
        if word.isdigit():
            new_word = p.number_to_words(word)
            new_words.append(new_word)
        else:
            new_words.append(word)
    return new_words

def remove_stopwords(words):
    """Remove stop words from list of tokenized words"""
    return [w for w in words if w not in stopwords.words('english')]

def stem_words(words):
    """Stem words in list of tokenized words"""
    stemmer = PorterStemmer()
    return [stemmer.stem(w) for w in words]

def lemmatize_verbs(words):
    """Lemmatize verbs in list of tokenized words"""
    lemmatizer = WordNetLemmatizer()
    return [lemmatizer.lemmatize(w, pos='v') for w in words]

def normalize(words):
    #words = remove_non_ascii(words) #NEEDS TO BE TESTED FOR ISSUER NAME
    words = to_lowercase(words)
    #words = remove_punctuation(words)
    words = remove_punctuation_whole(words)
    #words = replace_numbers(words)
    words = remove_stopwords(words)
    words = stem_words(words)
    #words = lemmatize_verbs(words)
    return words

def nltk_normalize(text):
    return normalize(word_tokenize(text))
