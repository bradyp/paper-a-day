# document: abstractText
#  references
# convert abstractText into a stop-word free document.
#=> generate a set of stop words that are super common.
#=> lda the stop words


class TopicModeller(object):
    def __init__(self):
        self.eyedee =2

    def map_to_citationspace(self, document):
        ''' given a dictionary representing a document,
        convert that document to citation / reference space by
        making a text document with text = to the citiaton and refernece id's.
        this maps the idea that our lda will be taken over the citations in the document.
        '''

    def map_to_abstracttitlespace(self, document):
        ''' given a dictionary representing a document,
        convert that document into "abstract title space" which gives
        a text entry and corresponding ID '''
