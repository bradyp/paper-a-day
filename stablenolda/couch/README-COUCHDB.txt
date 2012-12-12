CouchDB access
URI to database is https://vertex.skizzerz.net:6984/papers
Anonymous (logged out) users have read only access to db
Users with "paperaday" role have write access to db

Web UI may be accessed at https://vertex.skizzerz.net:6984/_utils for easy browsing,
otherwise the following views are available for use (with more to come as we fulfill
project requirements):
== Every document ==
Pretty self-explanatory, returns every document in the database
https://vertex.skizzerz.net:6984/papers/_all_docs

== Checkpoint 1 ==
These views were used to generate the charts for the data checkpoint, they list
the number of citations/references as the key, and the number of documents with that
many citations/references as the value, for an aggregate overview on the corpus of documents
https://vertex.skizzerz.net:6984/papers/_design/citecount/_view/all?group=true 
https://vertex.skizzerz.net:6984/papers/_design/refscount/_view/all?group=true

== Missing data ==
Mostly for internal purposes so we know what areas to expand upon in the future to attempt
to get as much working data as possible, this lists documents with either 0 citations,
0 references, or both. This was used to grab a list to populate the citation and reference
list initially based on the document's metadata.
https://vertex.skizzerz.net:6984/papers/_design/missingdata/_view/all (cites = 0 OR refs = 0)
https://vertex.skizzerz.net:6984/papers/_design/missingdata/_view/both (cites = 0 AND refs = 0)
https://vertex.skizzerz.net:6984/papers/_design/missingdata/_view/citations (cites = 0)
https://vertex.skizzerz.net:6984/papers/_design/missingdata/_view/references (refs = 0)

== Future passes ==
Future normalization passes will ensure that for every citation, there is a valid back reference,
and for every reference, there is a valid back citation, as it seems that the data pulled from
ACM lacks this, which forces some workarounds in the HITS algorithm (namely maintaining an
adjacency matrix). Additionally, for documents where full data was not retrieved (e.g. the document
was automatically generated due to an unlinked reference), I am planning on automating a search
of the ACM portal for that paper title to see if it would be possible to link that paper up to
a full document information set. Finally, views will be added that allow for splitting up documents
by overarching topics and finer topics, as well as allowing the searching thereof.