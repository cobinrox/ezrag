import os
import sys
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Add the parent directory to sys.path
sys.path.append(parent_dir)
from utils import utils
from utils import safeprint

import shutil
import fitz
import numpy as np
import torch
from transformers import pipeline,AutoTokenizer, AutoModelForCausalLM
from ragabs.absvectorsearcher import AbsVectorSearcher
import faiss

# Implement the Retriever using 
# naive chunking      for chunking
# SentenceTransformer for embeddings
# faiss               for searching
#class Faiss_Cosine(AbsVectorSearcher):
class Faiss_Cosine(faiss.IndexFlatIP):    
    def __init__(self, embeddingsShape):
        utils.print_start_msg("Initialize Faiss_Cosine ...")
        super().__init__(embeddingsShape)
        #self.faiss = faiss.IndexFlatIP(embeddingsShape)

    #def add(self,embeddings):
    #    self.faiss.add(embeddings)
    #def search(self,query_embedding, top_k):
    #    self.faiss.search(query_embedding,top_k)
    #def get_xb(self):
    #    return self.faiss.get_xb()
