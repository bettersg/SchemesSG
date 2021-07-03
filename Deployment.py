#!/usr/bin/env python
# coding: utf-8

# In[125]:


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
counter = 0

with open('scaler.pkl', 'rb') as handle:
    scaler = pickle.load(handle)
    
def scale(x, low = scaler['low'], high = scaler['high'], scaler = scaler):
    '''To automatically rescale results as new queries & descriptions come in
    I've currently bounded the range to ≈(min - 2σ, max + 2σ) to be safe
    Not sure if this is the best way; maybe environmental variables would be better(?)'''
    
    index = (x >= low) & (x <= high)
    if index.all():
        return (x - low) / (high - low) * 100
    
    if min(x) < low:
        scaler['low'] = low = max(min(x), -15)
        
    if max(x) > high:
        scaler['high'] = high = min(max(x), 14)
        
    with open('scaler1.pkl', 'wb') as handle:
        pickle.dump(scaler, handle, protocol = pickle.HIGHEST_PROTOCOL)
            
    x = (x - low) / (high - low)
    x[x < low] = 0.0
    x[x > high] = 1.0
    return x  * 100

def query_models(search, x = 0, biencoder = biencoder, crossencoder = crossencoder, emb = emb, df = df):
    '''Takes a user search, returns top 3 results of cross encoder & 1 randomly selected result of roBERTa'''
    # First query the cross encoder
    global counter
    cross_sim = crossencoder.predict([(search, i) for _, i in df[['Description']].itertuples()]) # Wall time ≈ 0.4s
    index = np.argsort(-sim)[:3]
    
    # Then query roBERTa
    query = biencoder.encode(search, convert_to_tensor = True)
    bi_sim = util.pytorch_cos_sim(query, emb)
    # Get top 3 similarities
    bi_sim = np.argsort(-bi_sim.cpu()[0])[:3]
    # Filter out similarities already returned by cross encoder & randomly pick 1
    bi_sim = np.random.choice(np.setdiff1d(bi_sim, index))
    
    index = np.append(index, bi_sim)
    relevance = scale(cross_sim[index])
    
    output = df.iloc[index, :5]
    output['Relevance'] = relevance
    output = output[output['Relevance'] > x]
    output = output[['Relevance','Scheme','Description', 'Agency', 'Image', 'Link']]
    
    jsonobject = output.to_json(orient = 'records')
    counter += 1
    jsonobject = {
        "number_requests_till_date": counter,
        "data": json.loads(jsonobject) 
    }
    return jsonobject


# In[ ]:




