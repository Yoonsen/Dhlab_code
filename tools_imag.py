import dhlab as dh
import dhlab.api.dhlab_api as api
import pandas as pd
import dhlab.graph_networkx_louvain as gnl
import networkx as nx
import requests
import json
from io import StringIO

def imag_corpus():
    res =  requests.get(f"{dh.constants.BASE_URL}/imagination/all")
    if res.status_code == 200:
        data = json.loads(res.text)
    else:
        data = "[]"
    return pd.DataFrame(data)

def geo_locations(dhlabid):
    res = requests.get(f"{dh.constants.BASE_URL}/imagination_geo_data", params={"dhlabid":dhlabid})
    if res.status_code == 200:
        data = pd.read_json(StringIO(res.text))
    else:
        data = pd.DataFrame()
    return data
                       

def get_imag_corpus():
    im = imag_corpus()
    c = dh.Corpus()
    c.extend_from_identifiers(im.urn)
    corpus = c.frame
    corpus.dhlabid = corpus.dhlabid.astype(int)
    return corpus

def make_collocation_graph(corpus, target_word, top=15, before=4, after=4, ref = None, limit=1000):
    """Make a cascaded network of collocations ref is a frequency list"""
    

    coll = dh.Collocations(corpus, [target_word], before=before, after=after, samplesize=limit).frame
    
    if not ref is None:
        coll['counts'] = coll['counts']*100/coll['counts'].sum()
        coll['counts'] = coll['counts']/ref
        
    coll = coll.sort_values(by="counts", ascending = False)
    edges = []
    visited = []               
    for word in coll[:top].index:
        # loop gjennom kollokasjonen og lag en ny kollokasjon for hvert ord
        edges.append((target_word, word, coll.loc[word]))
        if word.isalpha() and not word in visited:
            subcoll = dh.Collocations(corpus, [word], before=before, after=after, samplesize=limit).frame        
            if not ref is None:
                subcoll['counts'] = subcoll['counts']*100/subcoll['counts'].sum()
                subcoll['counts'] = subcoll['counts']/ref

            for w in subcoll.sort_values(by="counts", ascending = False)[:top].index:
                if w.isalpha():
                    edges.append((word, w, subcoll.loc[w]))
            visited.append(word)
            #print(visited)
    target_graph = nx.Graph()
    target_graph.add_edges_from(edges)

    return target_graph

def make_imagination_corpus():
    """Bygg hele imagination-korpuset fra dhlab"""
    return get_imag_corpus()

def imagination_ngram(corpus, words, mode='rel'):
    cnts = api.get_document_frequencies(list(corpus.urn), words = words)
    d2y = pd.Series(corpus.set_index('dhlabid')['year'].to_dict())
    d2y.to_frame('year')
    if mode.startswith('r') or mode.startswith('R'):
        df = cnts['relfreq']
        frek = df.transpose().copy()
        frek = pd.concat([frek, d2y.to_frame('year')], axis = 1).groupby('year').mean()
    else:
        df = cnts['freq']
        frek = df.transpose().copy()
        frek = pd.concat([frek, d2y.to_frame('year')], axis = 1).groupby('year').sum()
    return frek