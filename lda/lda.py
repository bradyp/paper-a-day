# document: abstractText
#  references
# convert abstractText into a stop-word free document.
#=> generate a set of stop words that are super common.
#=> lda the stop words

import string

# responsible for modelling topics.
# Code name it milan for a fashion reference
class TopicModeller(object):
    def __init__(self):
        self.eyedee =2


    # these are some cutesy methods to abstract away
    # the dictionary references for when I need to change them
    # :D
    def _citations(self, doc):
        return doc['citations']

    def _references(self, doc):
        return doc['references']

    def _title(self, doc):
        return doc['title']

    def _abst(self, doc):
        return doc['abstract']

    def _eyedee(self, doc):
        return doc['id']

    def map_to_citation(self, document):
        ''' given a dictionary representing a document,
        convert that document to citation / reference space by
        making a text document with text = to the citiaton and refernece id's.
        this maps the idea that our lda will be taken over the citations in the document.
        '''
        ref_and_cite = self._references(document) + self._citations(document)
        print document
        eyedee = self._eyedee(document)

        citation_texts = ' '.join(map(str,ref_and_cite))
        return {'id':eyedee, 'document':string.strip(citation_texts)}

    def map_to_abst(self, document):
        ''' given a dictionary representing a document,
        convert that document into "abstract title space" which gives
        a text entry and corresponding ID '''

        abst_title = [self._title(document), self._abst(document)]
        abst_title_text = ' '.join(map(str, abst_title))
        eyedee = self._eyedee(document)

        return {'id':eyedee, 'document':string.strip(abst_title_text)}

