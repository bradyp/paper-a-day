#!/usr/bin/env python

import collections
import math
import operator
import gensim
import re

import numpy as np
from scipy import sparse

from stemming import porter2

TEST_DOCS = [
    {
        "id":1,
        "citations":  [5],
        "references": [3, 2],
        "keywords": ["asdf"]
    },
    {
        "id":2,
        "citations":  [],
        "references": [1, 5],
        "keywords": []
    },
    {
        "id":3,
        "citations":  [5],
        "references": [1],
        "keywords": []
    },
    {
        "id":5,
        "citations":  [2],
        "references": [3],
        "keywords": []
    },
    {
        "id":314159,
        "citations":  [],
        "references": [],
        "keywords": []
    }
    ]


from stemming import porter2


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
      
    def _adjacencies(self):
        adjacencies = collections.defaultdict(set)
        for doc in self.docs:
            for refid in self.docs[doc]['references']:  #"who does this reference?"
                to = refid
                frm = doc
                # avoid self-references (of same paper)
                if frm!=to:
                    adjacencies[frm].add(to)
                # make sure that everyone who is mentioned is in the dict
                adjacencies[to]
            for citid in self.docs[doc]['citations']:   #"who cites this?"
                to = doc
                frm = citid
                # avoid self-citations (of same paper)
                if frm!=to:
                    adjacencies[frm].add(to)
                # make sure that everyone who is mentioned is in the dict
                adjacencies[to]
        return adjacencies
    
    def _matrix(self, adjacencies, uids):
        # create the sparse matix as a list of lists
        trans_prob = sparse.lil_matrix((len(adjacencies),len(adjacencies)))
        
        for src,links in adjacencies.iteritems():
            if not links:
                continue
            row = uids[src]
            row_val = 1.0 
            for dest in links:
                trans_prob[row, uids[dest]] = row_val
        # convert the lil_matrix to a csc_matrix, because it is better for doing
        # calculations
        return sparse.csc_matrix(trans_prob)

    #run HITS over an iterator of dicts
    def run_hits(self, G, k = 20):
    
        self.setup_hits()
        
        while(not self._has_converged()):
            self._hits_iteration()
        
        #store the authority values
        for i in range(len(adjacencies)):
            print i
    
        #G is a set of docids
#        for p in G:
 #         self.docs[p]['auth'] = 1  #self.docs[p]['auth'] is the authority score of the page p
  #        self.docs[p]['hub'] = 1 #self.docs[p]['hub'] is the hub score of the page p

#        for step in range(0, k):  #run the algorithm for k steps
 #         for p in G:  #update all authority values first
  #          self.docs[p]['auth'] = sum(self.docs[q]['hub'] for q in self.docs[p]['citations'])

#          for p in G:  #then update all hub values
 #           self.docs[p]['hub'] = sum(self.docs[r]['oldauth'] for r in self.docs[p]['references'])

    def setup_hits(self):
        adjacencies = self._adjacencies()
        uids = adjacencies.keys()
        self.uid_index = {uid:i for i,uid in enumerate(uids)}
    
        self.citeref_mat = self._matrix(adjacencies, self.uid_index)
        
        self.delta = 1
        adj_size = len(self._adjacencies())
        self.hub_vect = sparse.csc_matrix(np.ones(adj_size)).transpose()
        self.auth_vect = sparse.csc_matrix(np.ones(adj_size)).transpose()
        print self.hub_vect
        
    def _hits_iteration(self):
        old_auth = self.auth_vect
        old_hubs = self.hub_vect
        self.auth_vect = self.citeref_mat.transpose() * self.hub_vect
        self.hub_vect = self.citeref_mat * self.auth_vect
        
        print self.auth_vect
        print self.hub_vect
        self.delta = np.sum(np.array(old_auth-self.auth_vect+old_hubs-self.hub_vect))
        

    def _has_converged(self):
        return self.delta < 1e-6


    def index_docs(self, docs):
        for doc in docs:
          id = doc['id']
          self.docs[id] = doc
          # we make a set of the tokens to remove duplicates
          tokens = set(tokenize(doc['keywords']))
          for token in tokens:
            self.index[token].add(id)


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
    
    #FIXME run lda on the new query

    tokens = tokenize([query])
    id_sets = [hits_obj.index[token] for token in tokens]
    if not id_sets or not all(id_sets):
      print "No matches found"
      return
    ids = reduce(operator.__and__,id_sets)

    matching_docs = [hits_obj.docs[id] for id in ids] #this is the root set

    #create set of only the docs that conform to the query topics or are directly connected to the query topics
    base_set = set()  #set of doc ids
    for doc in matching_docs:
      #calculate the base set
      base_set.add(doc['id']) #add the doc id to base_set
      base_set = base_set.union(set(doc['citations'])) #add the citations to base_set
      base_set = base_set.union(set(doc['references']))  #add the references to base_set

    hits_obj.run_hits(base_set, 5)
    ranked_docs = [hits_obj.docs[doc] for doc in hits_obj.docs if doc in base_set]
    ranked_docs = sorted(ranked_docs, key=operator.itemgetter('auth'), reverse=True)
    print ranked_docs
      
    print "Matching docs: "
    for doc in ranked_docs:
      print doc['id']

if __name__=="__main__":
    main() 
