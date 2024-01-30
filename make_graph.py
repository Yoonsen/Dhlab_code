import requests
import networkx as nx
url = "https://api.nb.no/dhlab/nb_ngram_galaxies/galaxies/query"

def word_graph(word = None, cutoff = 20, corpus = 'all'):
    """corpus = bok, avis or all"""

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
            source, target = (nodes[edge['source']]['name'].capitalize(), nodes[edge['target']]['name'].capitalize())
            if source.isalnum() and target.isalnum():
                edgelist += [(source, target, abs(edge['value']))]
        G.add_weighted_edges_from(edgelist)
        
    return G