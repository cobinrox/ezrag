import os
import sys
from abc import ABC, abstractmethod

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add the parent directory to sys.path
sys.path.append(parent_dir)
#from utils import utils
from utils import utils

class AbsVectorSearcher(ABC):

    def __init__(self, embeddings):
        self.embeddings = embeddings

 


