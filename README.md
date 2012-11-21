paper-a-day
===========

"A Paper a Day keeps your advisor at bay!"

In general, the structure of the project is as follows:

\rb -> Ruby code. Primarily the PDF-extract code here.
\util -> Scripts for utility. primarily whatever makes tasks easier
\java|python -> Probably the hadoop code to proc data
\couch|mongo -> scripts / etc for setting up, using couch|mogno, which ever one we settle on. 
\hits -> Python code to run the HITS algorithm
\crawler -> Java code to update MetaMetadata to parse crawled ACM texts

Execution instructions:
  HITS:
   Assuming working directory is \hits
   Non-sparse:
    > python hits.py
   Sparse:
    > python sparsehits.py
   Tests:
    > nosetests 
 
