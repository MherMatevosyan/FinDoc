print('Importing dependencies...')
import_path = 'C:\\Data_scraping\\Financial_documents_research\\'
import sys
sys.path.append(import_path)

import pandas as pd
from findoc.pdf2text import pdf2text
from findoc.find_image import find_image
from findoc.preproccesing import *
from findoc.normalizer import nltk_normalize
from tqdm import tqdm
import numpy as np
import itertools

import nltk

from keras.models import Sequential
from keras.layers import Dense, Embedding, Masking
from keras.layers import LSTM
from keras.preprocessing.sequence import pad_sequences
from keras_tqdm import TQDMCallback

print('Dependencies imported!','\n')
print('Preprocessing...')

# Testing list of pdfs
path = 'C:\\Data_scraping\\Financial_documents_research\\'

list_of_pdfs = ['XS0859920406.pdf',
                'XS1087831688.pdf',
                'XS1096443152.pdf',
                'XS1148169060.pdf',
                'XS1324446092.pdf',
                'XS1416471057.pdf',
                'XS1789699607.pdf',
                'XS1799062440.pdf',
                'FR0010948257.pdf']

# Converting pdfs to text
list_of_docs = []
for pdf in list_of_pdfs:
    try:
        text = pdf2text(path+pdf)
        if find_image(text) == 0:
            list_of_docs.append([text,pdf])
    except:
        continue
        
# For testing
test = 'the maturity date of this note is 12 August 2025. Remember to go to www.notes.org for more information.'
test_target = '2025-08-12'
list_of_docs.append([test,'test.pdf'])

# Making dataset for 3 appropriate pdfs
X = []
Y = []
target_values = ['2024-07-15','2022-11-24','2026-03-16', test_target]
for (doc,name),target in zip(list_of_docs,target_values):
    mdoc = find_mdate(doc,target)
    wdoc = nltk.word_tokenize(mdoc[0])
    bdoc = find_keyword_block(wdoc,mdate_list,50,True)
    tdoc = ' '.join([b[0] for b in bdoc])
    x = nltk_normalize(tdoc)
    y = find_target_value(x,target)[0]
    X.append(x)
    Y.append(y)

# Converting words to ids    
all_tokens = itertools.chain.from_iterable(X)
word_to_id = {token: idx for idx, token in enumerate(set(all_tokens))}
token_ids = np.array([np.array([word_to_id[token] for token in doc]) for doc in X])
vocab = len(word_to_id)

# Padding sequences
padded = pad_sequences(token_ids, padding='post')
max_len = padded.shape[1]

print('Preprocessing Done!','\n')

print('Building the Model...')

# Splitting data
X_train = padded[:3]
X_test = padded[3:]
Y_train = np.array(Y[:3])
Y_test = np.array(Y[3:])

# Build the model 
embedding_vector_length = 16 
model = Sequential() 
model.add(Masking(mask_value=0., input_shape=(max_len,)))
model.add(Embedding(vocab, embedding_vector_length, input_length=None)) 
model.add(LSTM(20)) 
model.add(Dense(1, activation='relu')) 
model.compile(loss='mean_squared_error',optimizer='adam', metrics=['mae', 'acc']) 
print(model.summary(),'\n') 

print('Fitting the Model...')

# Fitting model
model.fit(X_train, Y_train, verbose = 0, nb_epoch = 300,
          batch_size=3, callbacks=[TQDMCallback()])

print('\n\n','Model predictions','\n')

# Checking model predictions
pd_train = pd.DataFrame(columns = ['True','Predicted','Train/Test'])
pd_train['True'] = Y_train
pd_train['Predicted'] = model.predict(X_train)
pd_train['Train/Test'] = 'Train'
pd_test = pd.DataFrame(columns = ['True','Predicted','Train/Test'])
pd_test['True'] = Y_test
pd_test['Predicted'] = model.predict(X_test)
pd_test['Train/Test'] = 'Test'
pred = pd.concat([pd_train,pd_test], axis = 0)
pred.reset_index(inplace = True)
del pred['index']
print(pred)

