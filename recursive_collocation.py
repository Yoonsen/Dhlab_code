import dhlab as dh
import dhlab.graph_networkx_louvain as gnl
import networkx as nx

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

