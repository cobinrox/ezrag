import os
import sys

import numpy as np
from transformers import pipeline,AutoTokenizer, AutoModelForCausalLM
import faiss

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Add the parent directory to sys.path
sys.path.append(parent_dir)
from utils import utils

'''
    NOT READY FOR PRIME TIME.
    Eventually this is meant to be a FAISS implementation for COSINE initial search,
    but eh.
'''
class Faiss_Cosine(faiss.IndexFlatIP):    
    def __init__(self, embeddingsShape):
        utils.print_start_msg("Initialize Faiss_Cosine ...")
        super().__init__(embeddingsShape)
        #self.faiss = faiss.IndexFlatIP(embeddingsShape)
