#!/usr/bin/env python

import collections
import math
import operator
import gensim
import re

from stemming import porter2

TEST_DOCS = [
    {
        "id":1,
        "citations":  [5],
        "references": [3, 2],
        "keywords": ["asdf", "arbitrary", "latent direchlet"]
    },
    {
        "id":2,
        "citations":  [1, 5, 3],
        "references": [],
        "keywords": ["lda", "topic modelling", "most authoritative"]
    },
    {
        "id":3,
        "citations":  [5, 1],
        "references": [2],
        "keywords": [""]
    },
    {
        "id":5,
        "citations":  [],
        "references": [3, 2, 1],
        "keywords": ["pagerank", "the least authoritative"]
    },
    {
        "id":314159,
        "citations":  [57721],
        "references": [271828],
        "keywords": ["xyzzy"]
    }
    ]

def tokenize(text):
    """
    Take a string and split it into tokens on word boundaries.

    A token is defined to be one or more alphanumeric characters,
    underscores, or apostrophes.  Remove all other punctuation, whitespace, and
    empty tokens.  Do case-folding to make everything lowercase. This function
    should return a list of the tokens in the input string.
    """
    tokens = list()
    for entry in text:
      tokens = tokens + re.findall("[\w']+", entry.lower())
    return [porter2.stem(token) for token in tokens]

class HITS(object):

    def __init__(self):
      self.index = collections.defaultdict(set)
      self.docs = {}
      
    #run HITS over an iterator of dicts
    def run_hits(self, G, k = 20):
        #G is a set of docids
        for p in G:
          self.docs[p]['auth'] = 1  #self.docs[p]['auth'] is the authority score of the page p
          self.docs[p]['hub'] = 1 #self.docs[p]['hub'] is the hub score of the page p

        for step in range(0, k):  #run the algorithm for k steps
          for p in G:  #update all authority values first
            self.docs[p]['auth'] = sum(self.docs[q]['hub'] for q in self.docs[p]['citations'] and G)

          for p in G:  #then update all hub values
            self.docs[p]['hub'] = sum(self.docs[r]['auth'] for r in self.docs[p]['references'] and G)



    def index_docs(self, docs):
        for doc in docs:
          id = doc['id']
          self.docs[id] = doc
          # we make a set of the tokens to remove duplicates
          tokens = set(tokenize(doc['keywords']))
          for token in tokens:
            self.index[token].add(id)
            
    def setup_baseset(self, query):
        tokens = tokenize([query])
        id_sets = [self.index[token] for token in tokens]
        
        if not id_sets or not all(id_sets):
          print "No matches found"
          return
        ids = reduce(operator.__and__,id_sets)

        matching_docs = [self.docs[id] for id in ids] #this is the root set
        
        doc_ids = [doc for doc in self.docs]
        

        #create set of only the docs that conform to the query topics or are directly connected to the query topics
        base_set = set()  #set of doc ids
        for doc in matching_docs:
          #calculate the base set
          base_set.add(doc['id']) #add the doc id to base_set
          
          #TODO is there a way to get around tossing the non-captured ACM cites/refs?
          real_citations = set(doc['citations']).intersection(set(doc_ids))
          base_set = base_set.union(real_citations) #add the citations to base_set
          real_references = set(doc['references']).intersection(set(doc_ids))
          base_set = base_set.union(real_references)  #add the references to base_set
        return base_set


def get_query(fromCL = True):    ##allowing for possible changes to this later
    if fromCL:
        return input("Enter query: ")

def get_docs(useDefault = True):    ##pulling from test corpus for now
    if useDefault:
        return TEST_DOCS

def main():
    #snag the docs from whereever
    docs = get_docs()

    hits_obj = HITS()

    #make a set of all the stemmed keywords (tokens, more or less)
    hits_obj.index_docs(docs)

    #read queries
    query = get_query()
    
    #TODO run lda on the new query

    base_set = hits_obj.setup_baseset(query)

    hits_obj.run_hits(base_set, 5)
    
    ranked_docs = [hits_obj.docs[doc] for doc in hits_obj.docs if doc in base_set]
    ranked_docs = sorted(ranked_docs, key=operator.itemgetter('auth'), reverse=True)
      
    print "Top docs: "
    for doc in ranked_docs:
      print doc['id']

if __name__=="__main__":
    main() 
