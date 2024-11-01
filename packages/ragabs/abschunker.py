import os
import sys
from abc import ABC, abstractmethod

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add the parent directory to sys.path
sys.path.append(parent_dir)
#from utils import utils
from utils import utils

class AbsChunker(ABC):

    def __init__(self, name, docs_dir,chunk_size):
        self.chunk_size = chunk_size
        self.chunking_type = name
        self.docs_dir = docs_dir


    @abstractmethod
    def chunkThese(self, docs,chunk_size):
        pass

    def first_x_last_x_chars(self,chunk, n):
        first_n = chunk[:n]
        last_n = chunk[-n:]
        length = len(chunk)

        return f"[{first_n}]...[{last_n}]({length})"


