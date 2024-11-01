import os
import sys
from abc import ABC, abstractmethod

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add the parent directory to sys.path
sys.path.append(parent_dir)
#from utils import utils
from utils import utils

class AbsGenerator(ABC):

    def setSessionName(self, session_name):
        self.session_name = session_name
    def setDebug(self, debug):
        self.debug = debug        

    @abstractmethod
    def generate_response(self, query: str, context: list) -> str:
        """
        Generate a natural language response using the user query and retrieved documents.
        Input: raw query (str), list of context documents or document embeddings (list of str or embeddings)
        Output: generated response (str)
        """
        pass
