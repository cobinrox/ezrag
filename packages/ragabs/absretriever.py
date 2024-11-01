import os
import sys
from abc import ABC, abstractmethod

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
from utils import utils


utils.check_venv()
class AbsRetriever(ABC):
    EUCLIDIAN_DISTANCE = "EUCLIDIAN"
    DOT_PRODUCT_DISTANCE = "DOT_PRODUCT"
    
    @abstractmethod
    def _create_doc_embeddings(self):
        pass
    
    @abstractmethod
    def public_retrieve_documents(self, query: str, top_k: int = 5) -> list:
        pass
    #def retrieve(self,query:str):
    #    pass
