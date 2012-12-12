paper-a-day
===========

"A Paper a Day keeps your advisor at bay!"

\couch -> scripts / etc for setting up, using couch 
\hits -> Python code to run the HITS algorithm
\lda -> Python code to run the LDA algorithm for topic modelling
\crawler -> Java code to update MetaMetadata to parse crawled ACM texts
\stablenolda -> Stable HITS without LDA

Our project has two major components, with a floating set of code related to data and cleaning it up. In general: there's the HITS code w/ hubs and authorities goodness, and the LDA code which handles topic modelling. Both of these are integrated in serve.py, which runs LDA during initialization and HITS at query-time.

To run the HITS code: 
Assuming working directory is \hits
Non-sparse:
  > python hits.py
Sparse:
  > python sparsehits.py
Tests:
  > nosetests

To run the LDA code: 
1. Install GenSim '''sudo easy_install gensim''' 
2. Run the tests. :D 

To run the whole kit-and-kaboodle:
1. Install gensim
2. Install couchdb
3. Install numpy/scipy
4. Run serve.py
5. Goto localhost:8080 and query away
