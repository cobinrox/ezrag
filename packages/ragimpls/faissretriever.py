import os
import sys
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Add the parent directory to sys.path
sys.path.append(parent_dir)
#from utils import utils
#from packages.utils.utils import utils
from utils import utils
from utils import safeprint


utils.check_venv()

import shutil
import faiss
import fitz
import numpy as np
# utils.print_start_msg("importing SentenceTransformer")
# from sentence_transformers import SentenceTransformer
# utils.print_stop_msg("imported Sentencetransformer")
import torch

from ragabs.absretriever import AbsRetriever

# nasty syntax to allow vscode to run this file in python debugger
#sys.path.append('../utils')


# Implement the Retriever using 
# naive chunking      for chunking
# SentenceTransformer for embeddings
# faiss               for searching
class Naive_ST_FAISS_Retriever(AbsRetriever):
    #def __init__(self, index_dir: str, docs_dir: str, flush=True):
    def __init__(self, embedding_model_name: str = 'all-MiniLM-L6-v2',  docs_dir: str = 'documents',  chunk_size=512, 
                 persistent_embeddings_path: str = 'faiss_index', flush=True):
        utils.print_start_msg("Initialize ...")
        self.type_chunking_engine         = "naive"
        self.type_embedding_engine  = f"ST/{embedding_model_name}"
        self.type_vector_engine = "faiss"
        self.search_engine_distance_type = AbsRetriever.EUCLIDIAN_DISTANCE

        self.flush     = flush
        utils.print_start_msg("importing SentenceTransformer")
        from sentence_transformers import SentenceTransformer
        utils.print_stop_msg("imported Sentencetransformer")
        self.embedding_engine_model = SentenceTransformer(embedding_model_name)
        #self._quantize(self.model)
        if os.path.exists(docs_dir):
           self.docs_dir = docs_dir  # Directory containing documents
        else:
            utils.printf(f"Warning doc dir [{docs_dir}] not found.")
            self.docs_dir = None
        self.vector_engine = None
        self.persistent_embeddings_path = persistent_embeddings_path  # Path to store/load the FAISS index

        self.doc_chunks = []  # Store document text
        self.doc_chunks_names = []  # Store document names for retrieval
        self.doc_chunks_dicts = [] # to replace stupid arrays
        self.embeddings = None
        self.chunk_size = chunk_size  # Size of each chunk when initially loading docs

        # check if persisted vectors already exist and flush if desired
        if( self.flush):
            self._flush(self.persistent_embeddings_path)
        utils.print_stop_msg("...initialize")

    #def retrieve(self, query:str):
    #    self._create_doc_embeddings()
    #    #top_doc_names,top_chunks = retriever.public_retrieve_documents(query, top_k=5)
    #    return retriever.public_retrieve_documents(query, top_k=5)
    
    def _quantize(self, model):
        # Apply dynamic quantization to specific modules (e.g., Linear layers)
        self.quantized_model = torch.quantization.quantize_dynamic(
            model,
            {torch.nn.Linear},  # Specify the layers to be quantized
            dtype=torch.qint8   # Use 8-bit integer quantization
        )

        # Save the quantized model state_dict
        torch.save(self.quantized_model.state_dict(), 'quantized_sentence_transformer.pth')

        # To load the quantized model later
        quantized_model_loaded = SentenceTransformer('all-MiniLM-L6-v2')
        quantized_model_loaded.load_state_dict(torch.load('quantized_sentence_transformer.pth'))

        # self.quantized_model = torch.quantization.quantize_dynamic(
        #         model,
        #         {torch.nn.Linear},  # Specify the layers to be quantized
        #         dtype=torch.qint8   # Use 8-bit integer quantization
        #     )

        # # Save the quantized model
        # self.quantized_model.save('quantized_sentence_transformer')

        # # Now, load the quantized model for inference
        # self.quantized_model = SentenceTransformer('quantized_sentence_transformer')

    def _flush(self, path):
        utils.print_start_msg(f"flushing any persisted [{self.type_vector_engine}] embedding files...") 
        if os.path.isfile(path):
          try:
            os.remove(path)
            utils.printf(f"Deleted file: {path}")
          except Exception as e:
            utils.printf(f"Error deleting file {path}: {e}")
        elif os.path.isdir(path):
          try:
            shutil.rmtree(path)
            utils.printf(f"Deleted directory: {path}")
          except Exception as e:
            utils.printf(f"Error deleting directory {path}: {e}")
        utils.print_stop_msg(f"...flushing any persisted [{self.type_vector_engine}] embeddings") 
    def _persisted_embeddings_exist(self):
          return os.path.exists(self.persistent_embeddings_path)

    def _create_doc_embeddings(self):
        """
        Create a Faiss index for the loaded documents by embedding them into vectors.
        """
        # Load documents from directory
        self._load_n_chunk_docs()

        if len(self.doc_chunks_dicts) == 0:
            print("FYI- No documents to index.")
            

        # Convert the document chunks to embeddings
        utils.print_start_msg(f"embedding/encoding chunks via [{self.type_embedding_engine}]...")
        safeprint.safe_print_obj(self.embedding_engine_model,"embedder engine")
        embeddings = self.embedding_engine_model.encode(self.doc_chunks, show_progress_bar=False)
        utils.print_stop_msg(f"...embedding/encoding chunks via [{self.type_embedding_engine}]")
        
        # Create a Faiss index (L2 Euclidian distance)
        utils.print_start_msg(f"creating embedding store via [{self.type_vector_engine}]...")
        if(self.search_engine_distance_type == "EUCLIDIAN"):
            self.vector_engine = faiss.IndexFlatL2(embeddings.shape[1])
        elif self.search_engine_distance_type == "DOT_PRODUCT":
            self.vector_engine = faiss.IndexFlatIP(embeddings.shape[1])
        utils.print_stop_msg(f"...creating embedding store via [{self.type_vector_engine}]")
        
        # Add the embeddings to the Faiss index
        utils.print_start_msg(f"adding embeddings to embedding store [{self.type_vector_engine}]...")
        self.vector_engine.add(embeddings)
        utils.print_stop_msg(f"...adding embeddings to embedding store [{self.type_vector_engine}]")
        self.embeddings = embeddings
        # Persist the index to disk
        utils.print_start_msg(f"saving embeddings to disk as file [{self.persistent_embeddings_path}] for [{self.type_vector_engine}]...")
        faiss.write_index(self.vector_engine, self.persistent_embeddings_path)
        utils.print_stop_msg(f"...saving embeddings to disk for [{self.type_vector_engine}]")

    def _load_persisted_embeddings(self):
        """Load a persisted embedding store from disk."""
        if os.path.exists(self.persistent_embeddings_path):
            utils.print_start_msg(f"reading persisted embedding from [{self.persistent_embeddings_path}] for [{self.type_vector_engine}]...")
            self.vector_engine = faiss.read_index(self.persistent_embeddings_path)
            utils.print_stop_msg(f"...reading fais persisted embedding for [{self.type_vector_engine}]")
            self.embeddings = self.vector_engine.get_xb()  # get_xb() returns the stored vectors as a numpy array

        else:
            print(f"Programming error -- No previously persisted embeddings file found at {self.persistent_embeddings_path} for [{self.type_vector_engine}]. Please create the embeddings first.")

    def _extract_pdf_text(self, filepath: str) -> str:
        doc = fitz.open(filepath)
        text = ""
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            text += page.get_text()
        doc.close()
        return text
    def _chunk_text(self, text: str) -> list:
        """
        Split large document text into smaller chunks.
        Args:
            text: The document's full text.
        Returns:
            List of chunks (strings) from the document.
        """
        # Split the text into chunks of self.chunk_size characters
        return [text[i:i + self.chunk_size] for i in range(0, len(text), self.chunk_size)]
    
    def _load_n_chunk_docs(self):
        """
        Load and process all documents (PDF and TXT) from the docs directory.
        """
        fileCount = 0
        utils.print_start_msg(f"loading and chunking docs via [{self.type_chunking_engine}]...")
        for filename in os.listdir(self.docs_dir):
            fileCount = fileCount + 1
            filepath = os.path.join(self.docs_dir, filename)

            if filename.endswith(".txt"):
                # Process text files
                with open(filepath, 'r', encoding='utf-8') as file:
                    content = file.read()
                utils.printf(f"Loaded text file: {filename}")
            elif filename.endswith(".pdf"):
                # Process PDF files
                content = self._extract_pdf_text(filepath)
                utils.printf(f"Loaded PDF file: {filename}")
            else:
                utils.printf(f"Skipping unsupported file: {filename}")
                continue

            # Split the document into smaller chunks
            local_chunks = self._chunk_text(content)
            
            # Store the document chunks and their corresponding names
            # append the chunks of this doc to the total chunks list
            self.doc_chunks.extend(local_chunks)
            # For each chunk, we append the original document name (you can also add chunk numbers)
            self.doc_chunks_names.extend([filename] * len(local_chunks))
            for a_local_chunk in local_chunks:
                self.doc_chunks_dicts.append( 
                    {"name"          : f"chunk_{len(self.doc_chunks_dicts)}",
                    "value"          : a_local_chunk,
                    "filename"       : filename,
                     "time"          : "whatever",
                     "someotherInfo:": "whaeverelse" }
                )
            #safeprint.safe_print_obj(self.doc_chunks)
            #safeprint.safe_print_obj(self.doc_chunks_names)
            breakoint = 1
        utils.print_stop_msg(f"...loading docs via [{self.type_chunking_engine}], created [{len(self.doc_chunks_dicts)}] total chunks from [{fileCount}] files")
        safeprint.safe_print_obj(self.doc_chunks_dicts,"chunks as a dict")



    def public_retrieve_documents(self, query: str, top_k: int = 5) -> list:
        top_doc_names = []
        top_chunks = []
        if(self.docs_dir is not None):
            self._create_doc_embeddings()
    
            # Convert the query into a vector
            query_embedding = self.embedding_engine_model.encode([query])
            
            # Search the embeddings store for the nearest documents
            utils.print_start_msg(f"querying embeddings via [{self.type_chunking_engine}]/[{self.type_embedding_engine}]/[{self.type_vector_engine}]...")
            distances, indices = self.vector_engine.search(query_embedding, top_k)
            safeprint.safe_print_obj(distances, "search result distances")
            safeprint.safe_print_obj(indices, "search result inices")

            utils.print_stop_msg("...querying embeddings")
            
            # Return the top_k document filenames
            #top_doc_names   =  [self.doc_chunks_names[i] for i in indices[0]]
            
            start = 0
            stop = len(indices[0])
            for step in range(start, stop):
                i = indices[0][step]
                doc_name = self.doc_chunks_names[i]
                top_doc_names.append(doc_name)
                distance = distances[0][step]
                
                print(f"Resulting chunk {step + 1}/{stop}:")
                print(f"  Index: {i}")
                print(f"  Document name: {doc_name}")
                print(f"  Distance: {distance}")
                print(f"  Current top_doc_names: {top_doc_names}")
                print()       
            
            top_chunks = [self.doc_chunks[i] for i in indices[0]]

            #return [self.doc_chunks_names[i] for i in indices[0]]
        return top_doc_names,top_chunks

# Example usage

if __name__ == "__main__":
    utils.printf("Starting...")
    # Directory containing PDF and TXT files
    #emb_file = "../../data/faiss_index"
    emb_file       = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data','faiss_index'))

    #docs_directory = "../../docs"
    docs_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'docs'))

    # Initialize the retriever, passing its parameters
    retriever = Naive_ST_FAISS_Retriever(persistent_embeddings_path=emb_file,docs_dir=docs_directory,chunk_size=512,flush=True)
       
    # Create the embeddings with the documents in the directory
    
    if not retriever._persisted_embeddings_exist():
        retriever._create_doc_embeddings()

    retriever._load_persisted_embeddings() 
    # Query
    query = "What is the capital of France?"
    #top_docs = retriever.public_retrieve_documents(query, top_k=5)
    top_doc_names,top_chunks = retriever.public_retrieve_documents(query, top_k=5)

    print("Top retrieved documents:", top_doc_names)
    print("Top chunks :", top_chunks)