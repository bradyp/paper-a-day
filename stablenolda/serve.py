#!/usr/bin/env python
# web server for ACM digital library search
# You should not need to edit this file. Hopefully.

import time

import bottle
import hits.sparsehits as hits
import couchdb
import operator

_hits_obj = None

@bottle.route('/search')
def search(name='World'):
    global _searcher
    query = "default"
    query = bottle.request.query.query
    count = -1
    if bottle.request.query.count != '':
        count = int(bottle.request.query.count)
    start_time = time.time()
    
    #FIXME run lda on the new query

    tokens = hits.tokenize([query])
    id_sets = [_hits_obj.index[token] for token in tokens]

    #FIXME change id_sets to be all docs that match the topic

    if not id_sets or not all(id_sets):
      print "No matches found"
      end_time = time.time()
      return dict(tweets = [], count = 0, time = end_time - start_time)
    ids = reduce(operator.__and__,id_sets)

    matching_docs = [_hits_obj.docs[id] for id in ids] #this is the root set

    #create set of only the docs that conform to the query topics or are directly connected to the query topics
    base_set = set()  #set of doc ids
    for doc in matching_docs:
      #calculate the base set
      base_set.add(doc['id']) #add the doc id to base_set
      base_set = base_set.union(set(doc['citations'])) #add the citations to base_set
      base_set = base_set.union(set(doc['references']))  #add the references to base_set

    #remove the referenced/citing docs that aren't actually in our collection
    all_ids = [x['id'] for x in docs if 'id' in x]
    base_set = base_set.intersection(all_ids)
    
    _hits_obj.run_hits(base_set)
    ranked_docs = [_hits_obj.docs[doc] for doc in _hits_obj.docs if doc in base_set]
    ranked_docs = sorted(ranked_docs, key=operator.itemgetter('auth'), reverse=True)
    if count > 0:
        ranked_docs = ranked_docs[:count]
    #at this point, ranked docs is the subset of docs with 'auth' as a key
    
    for doc in ranked_docs:
        print doc['auth']
    
    
    end_time = time.time()

    return dict(
            tweets = ranked_docs,
            count = len(ranked_docs),
            time = end_time - start_time,
            )


@bottle.route('/')
def index():
    return bottle.static_file('index.html', root='static')


@bottle.route('/favicon.ico')
def favicon():
    return bottle.static_file('favicon.ico', root='static')


@bottle.route('/static/<filename:path>')
def server_static(filename):
    return bottle.static_file(filename, root='static')

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


if __name__=="__main__":
    #snag the docs from the server
    server = couchdb.client.Server(url='https://vertex.skizzerz.net:6984/')
    db = server['papers']
    result = db.view('all/all')
    docs = []
    for row in result:
        docs.append(row.value)

    _hits_obj = hits.sparseHITS()

    #index all the docs
    _hits_obj.index_docs(docs)
    
    #FIXME run lda on the docs

    #NOW READY FOR QUERIES
      
    bottle.run(host='localhost',
               port=8080,
               reloader=True)
