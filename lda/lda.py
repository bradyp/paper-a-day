# !/usr/bin/env python
# document: abstractText
#  references
# convert abstractText into a stop-word free document.
#=> generate a set of stop words that are super common.
#=> lda the stop words

import string
from gensim import corpora, models, similarities
from stemming.porter2 import stem

class MemoryEfficientCorpus(object):
    #todo: modify this to process better if needed

    def _tokenize(self, entry):
        intermed = map(stem,entry.lower().split())
        #TODO: more vibrant stopwords here plz
        stopwords = ['of', 'in', 'and', 'for', 'the', 'to', 'by', 'or','but','therefore','with','on','we','one','method','based','is','are','were','found','which','a','that', 'algorithm', 'this', 'these', 'those','use', 'data']
        stopwords = map(stem, stopwords)
        stopwords.append('a')
        self.sizeCheat = self.sizeCheat + 1
        return [val for val in intermed if val not in stopwords]

    def __init__(self, docs):
        self.ourDocs = docs
        self.sizeCheat = 0
        #Hold onto a list of words, their frequencies
        #also creates an id for each term
        print type(docs)
        self.dictionary = corpora.Dictionary(map(self._tokenize,map(lambda x: x['document'], docs)))

        self.dictionary.filter_extremes(no_below=5, no_above=0.8)

    # Creates a bag of words corpus. :D
    def __iter__(self):
        for doc in self.ourDocs:
            yield self.dictionary.doc2bow(self._tokenize(doc['document']))

    def __len__(self):
        return self.sizeCheat

    def get_doc2bow(self, doc):
        return self.dictionary.doc2bow(self._tokenize(doc))


# responsible for modelling topics.
# Code name it milan for a fashion reference
class TopicModeller(object):
    def __init__(self):
        self.eyedee =2

    # these are some cutesy methods to abstract away
    # the dictionary references for when I need to change them
    # :D


    def _getVal(self, val, doc):
        try:
            return doc[val]
        except KeyError:
            return '0'

    def _citations(self, doc):
        return self._getVal('citations', doc)

    def _references(self, doc):
        return self._getVal('references', doc)

    def _title(self, doc):
        return self._getVal('title', doc)

    def _abst(self, doc):
        return self._getVal('abstract', doc)

    def _eyedee(self, doc):
        return self._getVal('id', doc)

    #yeah, these are really domain/our implementation specific
    #aspects of the implementation
    #since the dominant theory of our implementation
    #is that the two "topic spaces" for citations and abstracts will differ
    #we have two notions. The LDA code doesn't really care about that
    # and as we model citations wrt the id's, we can treat them like strings
    # and lda plays nicely

    #remember: LDA just maps strings within a document to hidden / latent
    #classes, so it doesn't matter if the strings are words proper
    #(which is traditional topic modelling)
    #or if they're words that represent an id.(which is trixy shenanigans ;P)

    def map_to_citation(self, document):
        ''' given a dictionary representing a document,
        convert that document to citation / reference space by
        making a text document with text = to the citiaton and refernece id's.
        this maps the idea that our lda will be taken over the citations in the document.
        '''

        ref_and_cite = self._references(document) + self._citations(document)
        eyedee = self._eyedee(document)
        citation_texts = ' '.join(map(str,ref_and_cite))

        return {'id':eyedee, 'document':string.strip(citation_texts)}

    def map_to_abst(self, document):
        ''' given a dictionary representing a document,
        convert that document into "abstract title space" which gives
        a text entry and corresponding ID '''

        abst_title = [self._title(document), self._abst(document)]
        abst_title_text = ' '.join(map(lambda x: x.encode('ascii', 'ignore'), abst_title))
        print document.keys()
        eyedee = self._eyedee(document)


        return {'id':eyedee, 'document':string.strip(abst_title_text)}

    def create_corpora(self, documents, mapping):
        return MemoryEfficientCorpus(map(mapping, documents))

    def lda_transform(self, corpora, topics=10):
        lda = models.ldamodel.LdaModel(corpora, num_topics=topics)
        return lda

    def setup_lda(self, dociter):
        self.our_corpora = self.create_corpora(dociter, self.map_to_abst)
        self.lda_model = self.lda_transform(self.our_corpora, topics =10)
        #create core LDA model.

    def check_model(self, item):
        itembow = self.our_corpora.get_doc2bow(item)
        return self.lda_model[itembow]

    def pick_topic(self, item):
        topicprobs = self.check_model(item)
        maxVal = 0;
        maxID = 0;
        for topic in topicprobs:
            eyedee, val = topic
            if val > maxVal:
                maxVal = val
                maxID = eyedee

        return maxID
#rec_titles_and_abstracts
#topics_titles_And_abstracts
