import pickle
import json
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer, util
from spellchecker import SpellChecker

df = pd.read_csv('df.csv')

model = SentenceTransformer('paraphrase-mpnet-base-v2')

with open('emb.pkl', 'rb') as handle:
    emb = pickle.load(handle)

spell = SpellChecker()
# Add words to vocabulary. Can continue adding as new queries come in, but would advise not to go too far; may inadvertently generate a lot of false positives
add = ['msf', 'sso', 'comcare', 'nkf', 'declutter', 'kikuchi', 'covid', 'covid-19', 'covid19', 'serangoon', 'sengkang', 'hougang', 'sinda', 'bukit', 'panjang', 'ubi',
       'taman', 'jurong', 'yishun', '4d']
spell.word_frequency.load_words(add)

def autocorrect(text):
    '''If text was autocorrected, function returns a tuple. Else, returns None
    Mostly works if only 1 character was wrong. Wall time is 160 - 170ms
    Cannot autocorrect words with punctuation in between (mostly typos in contractions, e.g. "havn't")
    Singaporean/ethnic words/names may be autocorrected into something else; medical terms may be corrected insensitively, e.g. "Kikuchi" into "kimchi"'''
    
    tokens = text.split()
    corrected_text = ''
    correction = False
    
    punctuation = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
    
    for _, word in enumerate(tokens):
        # Sadly spellchecker strips punctuation away, so strip them first, then insert back after spellchecking
        punctuation_front = punctuation_back = ''
        while word[-1] in punctuation:
            punctuation_back = word[-1] + punctuation_back
            word = word[:-1]

        while word[0] in punctuation:
            punctuation_front += word[0]
            word = word[1:]

        corrected_word = spell.correction(word)
        if corrected_word != word:
            correction = True

        corrected_text += punctuation_front + corrected_word + punctuation_back + ' '

    if correction:
        return corrected_text[:-1], text
    else:
        return None
    
def scale(x):
    '''Takes (arrays of) numbers between -1 to 1, scales to be between 0 to 100'''
    return (x + 1) / 2 * 100

def search_similar_schemes(text, relevance = 0, n = 5, spellcheck = True):
    '''Takes a user search, returns top n results. "relevance" is the relevance score threshold (from the old API)'''
    
    text = str(text).strip()
    
    search = text
    if spellcheck:
        temp = autocorrect(text)
        if isinstance(temp, tuple):
            search, _ = temp
    
    query = model.encode(search)
    sim = util.pytorch_cos_sim(query, emb)
    sim = np.array(sim[0])
    index = np.argsort(-sim)[:n]
    
    # Get relevance scores & filter df
    sim = scale(sim[index])
    df_out = df.iloc[index, :5]
    df_out['Relevance'] = sim
    df_out = df_out.loc[df_out['Relevance'] > relevance, ['Relevance', 'Scheme', 'Description', 'Agency', 'Image', 'Link']]
    
    jsonobject = df_out.to_json(orient = 'records')
    # Might wanna include some indicator here for front-end to say something like "Showing results for <search>. Search for <text> instead."
    return {'data' : json.loads(jsonobject)}
