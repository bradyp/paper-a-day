paper-a-day
===========

"A Paper a Day keeps your advisor at bay!"

Checkpoint 2 readme: 

\rb -> Ruby code. Primarily the PDF-extract code here.
\util -> Scripts for utility. primarily whatever makes tasks easier
\java|python -> Probably the hadoop code to proc data
\couch|mongo -> scripts / etc for setting up, using couch|mogno, which ever one we settle on. 
\hits -> Python code to run the HITS algorithm
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


In general, the pieces of functionality left to implement are indexing topic models from the entire corpora (easy, a call to save) , performing some clusering on topic models (easy, leverage k-n-n or switch topic modelling algorithm to hdp which is non parametric), and then archiving HITS runs on archived clusters. (easy, run clusters, run hits, recieve glory). This work makes sense to tackle during the UI phase, since a certain design decision (the idea of using two
topic spaces, abstracts and citations) are based off of UI decisions (presenting some abstracts that match a given topic query to help disambiguate and provide better signals.) 
