#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pickle
from collections import Counter
import json
import numpy as np
import pandas as pd
import torch
from sentence_transformers import SentenceTransformer, util
from sentence_transformers.cross_encoder import CrossEncoder

df = pd.read_csv('df.csv')
emb = torch.load('embeddings.pt')
biencoder = SentenceTransformer('paraphrase-distilroberta-base-v2')
crossencoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-12-v2')
    
def scale(x):
    '''Cross encoder's output ranges from -11 to +11. This scales (arrays of) numbers to be between 0 to 100
    Automatically rescales results as new queries & descriptions come in. I've currently bounded the range to ≈(min - 2σ, max + 2σ) to be safe
    Not sure if this is the best way; maybe environmental variables would be better(?)'''
    
    with open('scaler.pkl', 'rb') as handle:
        scaler = pickle.load(handle)
    
    # If all similarity scores are within original range, scale as per usual
    index = (x >= scaler['low']) & (x <= scaler['high'])
    if index.all():
        return (x - scaler['low']) / (scaler['high'] - scaler['low']) * 100
    
    # If any similarity score exceeds the original range, update pickle file to reflect the new range
    if min(x) < scaler['low']:
        scaler['low'] = max(min(x), -15)
    if max(x) > scaler['high']:
        scaler['high'] = min(max(x), 14)
    with open('scaler.pkl', 'wb') as handle:
        pickle.dump(scaler, handle, protocol = pickle.HIGHEST_PROTOCOL)
    
    # Then scale data according to new range
    x = (x - scaler['low']) / (scaler['high'] - scaler['low'])
    x[x < scaler['low']] = 0.0
    x[x > scaler['high']] = 1.0
    return x  * 100

def query_models(search, x = 0, biencoder = biencoder, crossencoder = crossencoder, emb = emb, df = df):
    '''Takes a user search, returns top 3 results of cross encoder & 1 randomly selected result of roBERTa
    x is the relevance score threshold (just following the old API)'''
    
    search = str(search.strip())
    
    # First query the cross encoder
    cross_sim = crossencoder.predict([(search, i) for _, i in df[['Description']].itertuples()]) # Wall time ≈ 0.4s
    index = np.argsort(-cross_sim)[:3]
    
    # Then query roBERTa
    query = biencoder.encode(search, convert_to_tensor = True)
    bi_sim = util.pytorch_cos_sim(query, emb)
    # Get top 3 similarities, filter those already returned by cross encoder, then randomly pick 1 & append
    bi_sim = np.argsort(-bi_sim.cpu()[0])[:3]
    bi_sim = np.random.choice(np.setdiff1d(bi_sim, index))
    index = np.append(index, bi_sim)
    
    # Get relevance scores & filter df
    relevance = scale(cross_sim[index])
    output = df.iloc[index, :5]
    output['Relevance'] = relevance
    output = output[output['Relevance'] > x]
    output = output[['Relevance','Scheme','Description', 'Agency', 'Image', 'Link']]
    
    jsonobject = output.to_json(orient = 'records')
    jsonobject = {
        "data": json.loads(jsonobject) 
    }
    return jsonobject

