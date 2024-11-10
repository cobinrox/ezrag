import os
import sys
from abc import ABC, abstractmethod

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add the parent directory to sys.path
sys.path.append(parent_dir)
from utils import utils

'''
    Abstract class for a chunker.  A chunker chops up a directory of documents into flat text.
'''
class AbsChunker(ABC):

    '''
        Constructor.
        @param self Python idiom required for syntax.
        @param session contains configuration information such as the location of the docs to query,
                       and stats/results information
    '''
    def __init__(self, session):
        self.session      = session
        self.chunks     = [] # place holder for the raw chunks we'll create
        self.chunk_objs = [] # place holder for an array of chunk definition objects; this is like
                             # a look up table for the raw chunks, for each raw chunk of text, it'll
                             # have info like the file where the chunk came from, the offset within the
                             # file where it came from, and other stuff


    '''
        Public required implementation.  This is the main method you gotta provide.
        @param self Python idiom needed for syntax
    '''
    @abstractmethod
    def public_chunk_the_docs(self):
        pass


