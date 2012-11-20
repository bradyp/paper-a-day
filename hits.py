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
        "citations":  [],
        "references": [],
        "keywords": []
    },
    {
        "id":2,
        "citations":  [],
        "references": [],
        "keywords": []
    },
    {
        "id":3,
        "citations":  [],
        "references": [],
        "keywords": []
    },
    {
        "id":4,
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

    #run HITS over an iterator of dicts
    def run_hits(self, G, k = 20):
        for p in G:
          p['auth'] = 1  #p['auth'] is the authority score of the page p
          p['hub'] = 1 #p['hub'] is the hub score of the page p
           
        for step in range(0, k):  #run the algorithm for k steps
          norm = 0
          for p in G:  #update all authority values first
            p['auth'] = 0
            for q in p['citations']:  #p.citations is the set of pages that link to p
               p['auth'] += G[q]['hub']
            norm += math.pow(p['auth'], 2) #calculate the sum of the squared auth values to normalize
          norm = math.sqrt(norm)
          for p in G:  #update the auth scores 
            p['auth'] = p['auth'] / norm  #normalise the auth values
          norm = 0
          for p in G:  #then update all hub values
            p['hub'] = 0
            for r in p['references']: #p.references is the set of pages that p links to
              p['hub'] += G[r]['auth']
              norm += math.pow(p['hub'], 2) #calculate the sum of the squared hub values to normalize
          norm = math.sqrt(norm)
          for p in G:  #then update all hub values
            p['hub'] = p['hub'] / norm   #normalize the hub values
            
            
    def index_docs(self, docs):
        for doc in docs:
          id = doc['id']
          self.docs[id] = doc
          # we make a set of the tokens to remove duplicates
          tokens = set(tokenize(doc['keywords']))
          for token in tokens:
            self.index[token].add(id)

def main():
    #FIXME snag the docs from wherever
    docs = TEST_DOCS

    hits_obj = HITS()

    #make a set of all the stemmed keywords (tokens, more or less)
    hits_obj.index_docs(docs)

    #FIXME run lda on the keywords
    #FIXME be able to select multiple nums of topics
    #mm = gensim.corpora.MmCorpus('')
    #lda = gensim.models.ldamodel.LdaModel(corpus=mm, id2word=id2word, num_topics = 4, update_every=0, passes=20)

    #read queries until read "/q"
    while True:
      query = input("Enter query or \"/q\" to quit: ")
      if query == "/q":
        return
      #run lda on the new query
      #doc_lda = lda[query]
      
      tokens = tokenize([query])
      print tokens
      id_sets = [hits_obj.index[token] for token in tokens]
      if not id_sets or not all(id_sets):
          print []
          print "wtf"
      ids = reduce(operator.__and__,id_sets)
      
      matching_docs = [hits_obj.docs[id] for id in ids] #this is the root set
      
      #FIXME create an iterator of only the docs that conform to the query topics or are directly connected to the query topics
      base_set = set()  #set of doc ids
      for doc in matching_docs:
        #calculate the base set
        base_set.add(doc['id']) #add the doc id to base_set
        base_set.union(set(doc['citations'])) #add the citations to base_set
        base_set.union(set(doc['references']))  #add the references to base_set
      
      #FIXME use base_set ids to pull the corresponding docs
      
      hits_obj.run_hits(base_set, 5)
      print hits_obj.docs

if __name__=="__main__":
    main()
