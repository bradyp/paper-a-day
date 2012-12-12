paper-a-day
===========

"A Paper a Day keeps your advisor at bay!"

\couch -> scripts / etc for setting up, using couch 
\hits -> Python code to run the HITS algorithm
\lda -> Python code to run the LDA algorithm for topic modelling
\crawler -> Java code to update MetaMetadata to parse crawled ACM texts

Currently our project is in two major components, with a floating set of code related to data and cleaning it up. In general: there's the HITS code w/ hubs and authorities goodness, and the LDA code which handles topic modelling. 

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

To run the whole kit-and-kaboodle: R
1. Run serve.py


