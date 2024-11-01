import os
import sys
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Add the parent directory to sys.path
sys.path.append(parent_dir)
from utils import utils
from utils import safeprint


utils.check_venv()

import shutil
import fitz
import numpy as np
import torch
from transformers import pipeline,AutoTokenizer, AutoModelForCausalLM
from ragabs.absgenerator import AbsGenerator

# Implement the Retriever using 
# naive chunking      for chunking
# SentenceTransformer for embeddings
# faiss               for searching
class TinyLLmGenerator(AbsGenerator):
    def __init__(self, model_name: str = 'TinyLlama/TinyLlama-1.1B-Chat-v1.0'):
        utils.print_start_msg("Initialize ...")
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(f"{model_name}")
        self.model = AutoModelForCausalLM.from_pretrained(model_name,torch_dtype=torch.float32)
        self.llm = pipeline("text-generation",model=self.model, tokenizer=self.tokenizer)

    def generate_response(self, query: str, chunks: list) -> str:
        utils.printf(f"DEBUG chunks being sent to gnerator llm: [{chunks}]")
        prompt = f"Context:{chunks}\n\nQuestion: {query}\n\nAnswer:"
        response = self.llm(prompt, max_length=1024,num_return_sequences=1)[0]['generated_text']
        safeprint.safe_print_obj(response,"llm response")
        return response.split("Answer:")[1].split("Context:")[0].strip()

    def _quantize(self, model):
        pass
# Example usage

if __name__ == "__main__":
    utils.printf("Starting...")

    # Initialize the retriever, passing its parameters
    generator = TinyLLmGenerator( )
       
    x = generator.generate_response("what is the captial of France","A cat has four legs. And a dog has four. And paris it the capital of france")
    utils.printf(f"The answer: [{x}]")
