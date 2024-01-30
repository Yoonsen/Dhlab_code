import dhlab as dh
import pandas as pd
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

def make_imagination_corpus():
    """Bygg hele imagination-korpuset fra dhlab"""

    import requests
    def query_imag_corpus(category=None, author=None, title=None, year=None, publisher=None, place=None, oversatt=None):
        """Fetch data from imagination corpus"""
        params = locals()
        params = {key: params[key] for key in params if params[key] is not None}
        #print(params)
        r = requests.get(f"{dh.constants.BASE_URL}/imagination", params=params)
        return r.json()
   
    # kategoriene
    cats = [
        'Barnelitteratur',
        'Biografi / memoar',
        'Diktning: Dramatikk',
        'Diktning: Dramatikk # Diktning: oversatt',
        'Diktning: Epikk',
        'Diktning: Epikk # Diktning: oversatt',
        'Diktning: Lyrikk',
        'Diktning: Lyrikk # Diktning: oversatt',
        'Diverse',
        'Filosofi / estetikk / språk',
        'Historie / geografi',
        'Lesebok / skolebøker / pedagogikk',
        'Litteraturhistorie / litteraturkritikk',
        'Naturvitenskap / medisin',
        'Reiselitteratur',
        'Religiøse / oppbyggelige tekster',
        'Samfunn / politikk / juss',
        'Skisser / epistler / brev / essay / kåseri',
        'Taler / sanger / leilighetstekster',
        'Teknologi / håndverk / landbruk / havbruk'
    ]
   
    # bygg en dataramme for hver kategori
    a = dict()
    for c in cats:
        a[c] = dh.Corpus()
        a[c].extend_from_identifiers(query_imag_corpus(category=c))
        a[c] = a[c].frame
        a[c]['category'] = c

    # lim alt sammen til et stort korpus
    imag_all = pd.concat([a[c] for c in a])
    imag_all.year = imag_all.year.astype(int)
    imag_all.dhlabid = imag_all.dhlabid.astype(int)
   
    return imag_all

def imag_ngram(corpus, words):
    cnts = dh.Counts(corpus, words)
    d2y = pd.Series(corpus.set_index('dhlabid')['year'].to_dict())
    d2y.to_frame('year')
    frek = cnts.frame.transpose().copy()
    frek = pd.concat([frek, d2y.to_frame('year')], axis = 1)
    return frek.groupby('year').sum()