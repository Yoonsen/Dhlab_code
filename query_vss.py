# Convert embeddings to sqlite

from IPython.display import Markdown
import pandas as pd
import os
import sqlite3

import numpy

import sqlite_vss

import matplotlib.pyplot as plt


class Connection():
    """manage connections to sqlite_vss
    con = Connection()
    con.connect(db)
    con.close(db)
    """
    
    def __init__(self, db):
        self.cons = dict()
        self.db = db
        con = sqlite3.connect(db)
        con.enable_load_extension(True)
        sqlite_vss.load(con)
        self.con = con
        print(f"connected to {db}")
        
    def close(self):
        self.con.close()
        print(f"closed connection to {self.db}")
        
def nearest(word, limit=20):
    with sqlite3.connect(db) as con:
        con.enable_load_extension(True)
        sqlite_vss.load(con)
        try:
            res = con.execute("""
            select b.word, a.distance from 
                (
                select rowid, distance from word_vectors
                where 
                    vss_search(
                        vector, 
                        (select vector from word_vectors where rowid = (select rowid from words where word = ?)))
                    limit ?
                ) as a, 
                words as b 
                where 
                    a.rowid = b.rowid""", (word, limit)).fetchall()
        except:
            res = []
    return res



def similar(con, word, limit = 20):
    try:
        res = con.execute("""
        select b.word, a.distance from 
            (
            select rowid, distance from word_vectors
            where 
                vss_search(
                    vector, 
                    (select vector from word_vectors where rowid = (select rowid from words where word = ?)))
                limit ?
            ) as a, 
            words as b 
            where 
                a.rowid = b.rowid
                
            order by distance asc""", (word, limit)).fetchall()
    except:
        res = []
    return res

def compare(con, w1, w2):
    try:
        res = con.execute("""
            select vss_cosine_similarity(
                    (select vector from word_vectors where rowid = (select rowid from words where word = ?)), 
                    (select vector from word_vectors where rowid = (select rowid from words where word = ?))
                )
         """, (w1, w2)).fetchall()
    except:
        res = []
    return res

class Dimensions():
    def __init__(self, con, dim1, dim2, words):
        self.dim1 = dim1
        self.dim2 = dim2
        self.words = words
        self.df = check_dimensions(con, dim1, dim2, words)

    def plot(self):
        dimplot(self.dim1, self.dim2, self.df)
        
def check_dimensions(gcon, dim1, dim2, words):
    df = []
    for dim in [dim1, dim2]:
        for word in words:
            try:
                df.append((dim, word, compare(gcon, dim, word)[0][0]))
            except:
                pass
    return pd.DataFrame(df).pivot(columns=0, values=2, index=1)            

def dimplot(dim1, dim2, df):
    
    plt.figure(figsize=(8, 6))
    plt.scatter(df[dim1], df[dim2])

    # Add labels
    for i in range(len(df)):
        plt.text(df[dim1].iloc[i], df[dim2].iloc[i], df.index[i])

    # Add crossbars along zero lines
    plt.axhline(0, color='grey', linewidth=0.8)
    plt.axvline(0, color='grey', linewidth=0.8)

    plt.xlabel(dim1)
    plt.ylabel(dim2)
    plt.title(f'Scatter Plot:{dim1} vs {dim2}')
    