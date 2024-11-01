import os
import sys
from abc import ABC, abstractmethod

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
from utils import utils


#utils.check_venv()
class AbsRetriever(ABC):
    #@TODO- move to absSearcher class
    EUCLIDIAN_DISTANCE   = "EUCLIDIAN"
    DOT_PRODUCT_DISTANCE = "DOT_PRODUCT"
    COSINE_DISTANCE      = "COSINE"

    STATS_SEARCH_HEADER  = "Session,SearchEngine,DistType,SearchScore,ChunkSize,ChunkFileName,OffsetInFile"
    
    def setSessionName(self, session_name):
        self.session_name = session_name
    def setDebug(self, debug):
        self.debug = debug        
    @abstractmethod
    def _create_doc_embeddings(self):
        pass
    
    @abstractmethod
    def public_retrieve_documents(self, query: str, top_k: int = 5) -> list:
        pass
    #def retrieve(self,query:str):
    #    pass

    @abstractmethod
    def injectChunker(self, chunker):
        pass
