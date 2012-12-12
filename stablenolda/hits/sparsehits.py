#!/usr/bin/env python

import collections
import math
import operator
import gensim
import re
import couchdb

import numpy as np
from scipy import sparse

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

class sparseHITS(object):

    def __init__(self):
      self.index = collections.defaultdict(set)
      self.docs = {}
      self.done = False
      
    def _adjacencies(self):
        adjacencies = collections.defaultdict(set)
        for doc in self.docs:
          if any(doc == seed for seed in self.seeds):  #can't check a non-existent doc
            for refid in self.docs[doc]['references']:  #"who does this reference?"
                to = refid
                frm = doc
                adjacencies[frm].add(to)
                # make sure that everyone who is mentioned is in the dict
                adjacencies[to]
            for citid in self.docs[doc]['citations']:   #"who cites this?"
                to = doc
                frm = citid
                # make sure that everyone who is mentioned is in the dict
                adjacencies[frm].add(to)
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
    def run_hits(self, base):
    
        self.seeds = base
        #set default scores for all docs
        for doc in self.seeds:
            self.docs[doc]['auth'] = 0
        if not self.setup_hits():
          return
        
        while(not self._has_converged()):
            self._hits_iteration()
        
       
        #store the authority values into the docs themselves
        sparse_indices = self.auth_vect.nonzero()[0]
        
        for uid in self.uid_index:
          if uid in self.docs:
           if self.uid_index[uid] in sparse_indices:
             self.docs[uid]['auth'] = self.auth_vect[self.uid_index[uid]].todense()[0,0]
           else:
             self.docs[uid]['auth'] = 0
        
    def setup_hits(self):
        adjacencies = self._adjacencies()
        if adjacencies == {}:
          return False
        uids = adjacencies.keys()

        self.uid_index = {uid:i for i,uid in enumerate(uids)}
    
        self.citeref_mat = self._matrix(adjacencies, self.uid_index)
        
        self.delta = 1
        adj_size = len(self._adjacencies())
        self.hub_vect = sparse.csc_matrix(np.ones(adj_size)).transpose()
        self.auth_vect = sparse.csc_matrix(np.ones(adj_size)).transpose()
        return True
        
    def _hits_iteration(self):
        old_auth = self.auth_vect.copy()
        old_hubs = self.hub_vect.copy()
        self.auth_vect = self.citeref_mat.transpose() * self.hub_vect
        self.hub_vect = self.citeref_mat * self.auth_vect
        
        self.auth_vect = self.auth_vect / math.sqrt(self.auth_vect.multiply(self.auth_vect).sum())
        self.hub_vect = self.hub_vect / math.sqrt(self.hub_vect.multiply(self.hub_vect).sum())
        
        auth_diff = old_auth - self.auth_vect
        hubs_diff = old_hubs - self.hub_vect
        auth_delta = auth_diff.multiply(auth_diff).sum()
        hubs_delta = hubs_diff.multiply(hubs_diff).sum()
        
        if auth_delta < 1e-6 and hubs_delta < 1e-6:  #we converged!
          self.done = True

    def _has_converged(self):
        return self.done


    def index_docs(self, docs):
        for doc in docs:
          if 'id' not in doc:
            continue    #not dealing with those docs
          id = doc['id']
          self.docs[id] = doc
          
          # we make a set of the tokens to remove duplicates
          wordlist = [word for word in doc['keywords'] if word != None]
          if doc['abstract'] != "An abstract is not available.":  #sad, but frequent
            wordlist.append(doc['abstract'])
          wordlist.append(doc['title'])  #everything has a title
          wordlist = wordlist + [word for word in doc['classification'] if word != None]
          
          tokens = set(tokenize([word for word in wordlist]))
          
          for token in tokens:
            self.index[token].add(id)


def get_query(fromCL = True):    ##allowing for possible changes to this later
    if fromCL:
        return input("Enter query: ")

def get_docs(useDefault = True):    ##pulling from test corpus for now
    if useDefault:
        server = couchdb.client.Server(url='https://vertex.skizzerz.net:6984/')
        db = server['papers']
        result = db.view('all/all')
        docs = []
        for row in result:
            docs.append(row.value)
        return docs

def main():
    #snag the docs from wherever
    docs = get_docs()

    hits_obj = sparseHITS()

    #index all the docs
    hits_obj.index_docs(docs)
    
    #FIXME run lda on the docs

    #NOW READY FOR QUERIES


    #read queries
    query = get_query()
    
    #FIXME run lda on the new query

    tokens = tokenize([query])
    id_sets = [hits_obj.index[token] for token in tokens]

    #FIXME change id_sets to be all docs that match the topic

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

    #remove the referenced/citing docs that aren't actually in our collection
    all_ids = [x['id'] for x in docs]
    base_set = base_set.intersection(all_ids)


    hits_obj.run_hits(base_set)
    ranked_docs = [hits_obj.docs[doc] for doc in hits_obj.docs if doc in base_set]
    ranked_docs = sorted(ranked_docs, key=operator.itemgetter('auth'), reverse=True)
      
    print "Matching docs: "
    for doc in ranked_docs:
      print doc['id']

if __name__=="__main__":
    main() 
