import dhlab as dh
import networkx as nx
import dhlab.graph_networkx_louvain as gnl
import requests
import pandas as pd
from collections import Counter

url = "https://api.nb.no/dhlab/nb_ngram_galaxies/galaxies/query"


def relaterte_ord(word, number = 20, recursive = 0):
    G = word_graph(word)
    res = pd.DataFrame(Counter(nx.eigenvector_centrality(G)).most_common(number), columns = ['word', 'score'])
    visited = []
    while recursive > 0:
        recursive -= 1
        for w in res.word:
            if not w in visited:
                visited.append(w)
                G = word_graph(w)
                part = pd.DataFrame(Counter(nx.eigenvector_centrality(G)).most_common(number), columns = ['word', 'score'])
                res = pd.concat([res, part]).drop_duplicates('word')
                
    res = res.sort_values(by='score', ascending = False)
    return res

def word_graph(word = None, cutoff = 20, corpus = 'all'):
    """ corpus = bok, avis or all"""
    params = {
        'terms':word, 
        'leaves':0,
        'limit':cutoff,
        'corpus':corpus,
    }
    r = requests.get(url, params = params)
    G = nx.DiGraph()
    edgelist = []
    if r.status_code == 200:
        #graph = json.loads(result.text)
        graph = r.json()
        #print(graph)
        nodes = graph['nodes']
        edges = graph['links']
        for edge in edges:
            source, target = (nodes[edge['source']]['name'], nodes[edge['target']]['name'])
            if source.isalnum() and target.isalnum():
                edgelist += [(source, target, abs(edge['value']))]
        G.add_weighted_edges_from(edgelist)
    return G