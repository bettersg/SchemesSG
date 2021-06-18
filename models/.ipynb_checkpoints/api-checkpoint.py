# Using this as the entry point to using the model
import json

import numpy as np
import torch
import pandas as pd
from sentence_transformers import SentenceTransformer, util


# ideally when starting up the flask app we load these into memory in a better way than just importing this lol
model = SentenceTransformer('paraphrase-distilroberta-base-v2')
df = pd.read_csv('../models/transformer/source_data.csv')
emb = torch.load('../models/transformer/embeddings.pt')


def return_query(sentence, embeddings, df, limit=50, rel_cap=0.2):
    query_emb = model.encode(sentence, convert_to_tensor=True)
    cos_sim = util.pytorch_cos_sim(query_emb, embeddings)
    cos_sim_series = pd.Series(cos_sim.numpy().flatten(), name='Relevance')
    return df.join(cos_sim_series[cos_sim_series >= rel_cap]).sort_values('Relevance', ascending=False).head(limit)[['Relevance','Scheme','Description', 'Agency', 'Image', 'Link']].to_json(orient="records")


def search_similar_schemes(search_term):
    global counter
    jsonobject = return_query(search_term, emb, df) #.encode('unicode-escape').decode('unicode-escape')
    counter = counter + 1
    jsonobject = { 
        "number_requests_till_date": counter,
        "data": json.loads(jsonobject) 
    }
    return jsonobject
