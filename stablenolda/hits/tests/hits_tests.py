#!/usr/bin/env python

import unittest
import operator

import hits

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
        "citations":  [7],
        "references": [3, 2, 1],
        "keywords": ["pagerank", "the least authoritative"]
    },
    {
        "id":314159,
        "citations":  [57721],
        "references": [271828],
        "keywords": ["xyzzy"]
    },
    {
        "id":7,
        "citations":  [9],
        "references": [5],
        "keywords": ["pr", "should not be found", "unless", "using 5's keywords"]
    },
    {
        "id":15,
        "citations":  [],
        "references": [7],
        "keywords": ["pr", "one level back"]
    }
    
    ]

class TestHITS(unittest.TestCase):
    def setUp(self):
        #snag the docs
        docs = TEST_DOCS

        self.hits_obj = hits.HITS()

        #make a set of all the stemmed keywords (tokens, more or less)
        self.hits_obj.index_docs(docs)

    def test_baseset(self):
        query = "asdf"  #docs 1, 2, 3, 5 are interlinked, so if one is found, all are found
        
        base_set = self.hits_obj.setup_baseset(query)
        self.assertEqual(base_set, set([1, 2, 3, 5]))
        
        query = "topic" #this is where it gets interesting with multi-word keywords
            #should they be treated as a single word? for here, they aren't. we'll see what LDA generates
        
        base_set = self.hits_obj.setup_baseset(query)
        self.assertEqual(base_set, set([1, 2, 3, 5]))
        
        query = "pagerank"  #base_set only expands once
        base_set = self.hits_obj.setup_baseset(query)
        self.assertEqual(base_set, set([1, 2, 3, 5, 7]))
        

    def test_strange_baseset(self):
        query = "xyzzy" #this doc only links to outside docs, which must be dropped for now
        
        base_set = self.hits_obj.setup_baseset(query)
        self.assertEqual(base_set, set([314159]))

    def test_hits(self):
        query = "asdf"  #docs 1, 2, 3, 5 are interlinked, so if one is found, all are found
        
        base_set = self.hits_obj.setup_baseset(query)
        self.hits_obj.run_hits(base_set, 5)
        ranked_docs = [self.hits_obj.docs[doc] for doc in self.hits_obj.docs if doc in base_set]
        ranked_docs = sorted(ranked_docs, key=operator.itemgetter('auth'), reverse=True)
        
        self.assertEqual(ranked_docs, [{'hub': 331776, 'auth': 82944, 'citations': [5], 'references': [3, 2], 'keywords': ['asdf', 'arbitrary', 'latent direchlet'], 'id': 1}, {'hub': 0, 'auth': 82944, 'citations': [1, 5, 3], 'references': [], 'keywords': ['lda', 'topic modelling', 'most authoritative'], 'id': 2}, {'hub': 331776, 'auth': 82944, 'citations': [5, 1], 'references': [2], 'keywords': [''], 'id': 3}, {'hub': 331776, 'auth': 82944, 'citations': [7], 'references': [3, 2, 1], 'keywords': ['pagerank', 'the least authoritative'], 'id': 5}])
        
        query = "topic" #this is where it gets interesting with multi-word keywords
            #should they be treated as a single word? for here, they aren't. we'll see what LDA generates
        
        base_set = self.hits_obj.setup_baseset(query)
        self.hits_obj.run_hits(base_set, 5)
        ranked_docs = [self.hits_obj.docs[doc] for doc in self.hits_obj.docs if doc in base_set]
        ranked_docs = sorted(ranked_docs, key=operator.itemgetter('auth'), reverse=True)
        
        self.assertEqual(ranked_docs, [{'hub': 331776, 'auth': 82944, 'citations': [5], 'references': [3, 2], 'keywords': ['asdf', 'arbitrary', 'latent direchlet'], 'id': 1}, {'hub': 0, 'auth': 82944, 'citations': [1, 5, 3], 'references': [], 'keywords': ['lda', 'topic modelling', 'most authoritative'], 'id': 2}, {'hub': 331776, 'auth': 82944, 'citations': [5, 1], 'references': [2], 'keywords': [''], 'id': 3}, {'hub': 331776, 'auth': 82944, 'citations': [7], 'references': [3, 2, 1], 'keywords': ['pagerank', 'the least authoritative'], 'id': 5}])
        
        query = "pagerank"  #base_set only expands once
        base_set = self.hits_obj.setup_baseset(query)
        self.hits_obj.run_hits(base_set, 5)
        ranked_docs = [self.hits_obj.docs[doc] for doc in self.hits_obj.docs if doc in base_set]
        ranked_docs = sorted(ranked_docs, key=operator.itemgetter('auth'), reverse=True)
        
        
        self.assertEqual(ranked_docs, [{'hub': 4000000, 'auth': 800000, 'citations': [5], 'references': [3, 2], 'keywords': ['asdf', 'arbitrary', 'latent direchlet'], 'id': 1}, {'hub': 0, 'auth': 800000, 'citations': [1, 5, 3], 'references': [], 'keywords': ['lda', 'topic modelling', 'most authoritative'], 'id': 2}, {'hub': 4000000, 'auth': 800000, 'citations': [5, 1], 'references': [2], 'keywords': [''], 'id': 3}, {'hub': 4000000, 'auth': 800000, 'citations': [7], 'references': [3, 2, 1], 'keywords': ['pagerank', 'the least authoritative'], 'id': 5}, {'hub': 4000000, 'auth': 800000, 'citations': [9], 'references': [5], 'keywords': ['pr', 'should not be found', 'unless', "using 5's keywords"], 'id': 7}])
    
    def test_strange_hits(self):
        query = "xyzzy" #this doc only links to outside docs, which must be dropped for now
        base_set = self.hits_obj.setup_baseset(query)
        self.hits_obj.run_hits(base_set, 5)
    
        ranked_docs = [self.hits_obj.docs[doc] for doc in self.hits_obj.docs if doc in base_set]
        ranked_docs = sorted(ranked_docs, key=operator.itemgetter('auth'), reverse=True)
        
        self.assertEqual(ranked_docs, [{'hub': 1, 'auth': 1, 'citations': [57721], 'references': [271828], 'keywords': ['xyzzy'], 'id': 314159}])


if __name__ == '__main__':
    unittest.main()
