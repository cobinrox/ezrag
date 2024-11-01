import os
import sys
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Add the parent directory to sys.path
sys.path.append(parent_dir)
#from utils import utils
#from packages.utils.utils import utils
from utils import utils
from utils import safeprint
from ragabs.abschunker import AbsChunker
from ragimpls.naievechunker import Naive_Chunker

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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
from packages.ragimpls.faisscosine import Faiss_Cosine

# nasty syntax to allow vscode to run this file in python debugger
#sys.path.append('../utils')


# Implement the Retriever using 
# naive chunking      for chunking
# SentenceTransformer for embeddings
# faiss               for searching
class Naive_ST_FAISS_Retriever(AbsRetriever):
    #def __init__(self, index_dir: str, docs_dir: str, flush=True):
    def __init__(self, embedding_model_name: str = 'all-MiniLM-L6-v2',  docs_dir: str = 'documents',  chunk_size=512, 
                 search_engine_distance_type = AbsRetriever.EUCLIDIAN_DISTANCE, persistent_embeddings_path: str = 'faiss_index', flush=True):
        utils.print_start_msg("Initialize ...")
        if os.path.exists(docs_dir):
           self.docs_dir = docs_dir  # Directory containing documents
        else:
            utils.printf(f"Warning doc dir [{docs_dir}] not found.")
            self.docs_dir = None
        self.type_chunking_engine        = "naive"
        self.type_embedding_engine       = f"ST/{embedding_model_name}"
        self.type_vector_engine          = "faiss"
        self.search_engine_distance_type = search_engine_distance_type #AbsRetriever.EUCLIDIAN_DISTANCE
        self.chunking_engine             = Naive_Chunker("naive",self.docs_dir,chunk_size)

        self.flush     = flush
        utils.print_start_msg("importing SentenceTransformer")
        from sentence_transformers import SentenceTransformer
        utils.print_stop_msg("imported Sentencetransformer")
        self.embedding_engine_model = SentenceTransformer(embedding_model_name)
        #self._quantize(self.model)
        self.vector_engine = None
        self.persistent_embeddings_path = persistent_embeddings_path  # Path to store/load the FAISS index

        self.chunks = []  # Store document text
        self.chunks_names = []  # Store document names for retrieval
        self.chunks_dicts = [] # to replace stupid arrays
        self.initial_chunk_embeddings = None
        self.chunk_size = chunk_size  # Size of each chunk when initially loading docs

        # check if persisted vectors already exist and flush if desired
        if( self.flush):
            self._flush(self.persistent_embeddings_path)
        
        self.stats_file = "STATS/rag_search_stats.csv"
        utils.print_stop_msg("...initialize")

    def injectChunker():
        pass
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
        # Load documents from directory
        self._load_n_chunk_docs()

        if len(self.chunks_dicts) == 0:
            print("FYI- No documents to index.")
            

        # Convert the document chunks to embeddings
        utils.print_start_msg(f"embedding/encoding chunks via [{self.type_embedding_engine}]...")
        #safeprint.safe_print_obj(self.embedding_engine_model,"embedder engine")
        embeddings = self.embedding_engine_model.encode(self.chunks, show_progress_bar=False)
        utils.print_stop_msg(f"...embedding/encoding chunks via [{self.type_embedding_engine}]")
        #safeprint.safe_print_obj(embeddings,"embeddings")

        # Create a Faiss searcher
        utils.print_start_msg(f"creating embedding store via [{self.type_vector_engine}]...")
        if(self.search_engine_distance_type == AbsRetriever.EUCLIDIAN_DISTANCE):
            self.vector_engine = faiss.IndexFlatL2(embeddings.shape[1])
        elif self.search_engine_distance_type == AbsRetriever.DOT_PRODUCT_DISTANCE:
            self.vector_engine = faiss.IndexFlatIP(embeddings.shape[1])
        elif self.search_engine_distance_type == AbsRetriever.COSINE_DISTANCE:
            self.vector_engine = Faiss_Cosine(embeddings.shape[1])
        utils.print_stop_msg(f"...creating embedding store via [{self.type_vector_engine}]")
        
        # Add the embeddings to the search db
        utils.print_start_msg(f"adding embeddings to embedding store [{self.type_vector_engine}]...")
        self.vector_engine.add(embeddings)
        utils.print_stop_msg(f"...adding embeddings to embedding store [{self.type_vector_engine}]")
        self.initial_chunk_embeddings = embeddings
        # Persist the embeddings to disk
        utils.print_start_msg(f"saving embeddings to disk as file [{self.persistent_embeddings_path}] for [{self.type_vector_engine}]...")
        faiss.write_index(self.vector_engine, self.persistent_embeddings_path)
        utils.print_stop_msg(f"...saving embeddings to disk for [{self.type_vector_engine}]")

    def _load_persisted_embeddings(self):
        """Load a persisted embedding store from disk."""
        if os.path.exists(self.persistent_embeddings_path):
            utils.print_start_msg(f"reading persisted embedding from [{self.persistent_embeddings_path}] for [{self.type_vector_engine}]...")
            self.vector_engine = faiss.read_index(self.persistent_embeddings_path)
            utils.print_stop_msg(f"...reading fais persisted embedding for [{self.type_vector_engine}]")
            self.initial_chunk_embeddings = self.vector_engine.get_xb()  # get_xb() returns the stored vectors as a numpy array

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
    
    # create list of chunks as dictionary lookup of chunks
    # and corresponding list of actual chunks
    def _load_n_chunk_docs(self):
        """
        Load and process all documents (PDF and TXT) from the docs directory.
        """
        fileCount = 0
        total_chunk_idx = 0
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
            self.chunks.extend(local_chunks)
            # For each chunk, we append the original document name (you can also add chunk numbers)
            #self.chunks_names.extend([filename] * len(local_chunks))
            local_chunk_offset_in_this_file = 0
            # a name to assign to the chunk for help in debugging
            # idx-- the numerical (0..n) piece of the chunk of all of our chunks we're collecting across all files
            #       and which is located within the chunks array
            # value of the chunk
            # a shortened text representation of the text in the chunk
            # length of the chunk
            # the file name where the chunk came from
            # the offset within the file where the chunk came from

            for a_local_chunk in local_chunks:
                self.chunks_dicts.append( 
                    {"name"          : f"chunk_{total_chunk_idx}", #f"chunk_{len(self.chunks_dicts)}",
                     "idx"           : total_chunk_idx, # len(self.chunks_dicts),
                     #"value"         : a_local_chunk,
                     "summary"       : self.chunking_engine.first_x_last_x_chars(a_local_chunk,3),
                     "len"           : len(a_local_chunk),
                     "filename"      : filename,
                     "offsetInFile"  : local_chunk_offset_in_this_file,
                     "time"          : "whatever",
                     "someotherInfo:": "whaeverelse",
                     "score"         : -1 }
                )
                local_chunk_offset_in_this_file = local_chunk_offset_in_this_file + len(a_local_chunk)
                total_chunk_idx = total_chunk_idx+1
            #safeprint.safe_print_obj(self.chunks)
            #safeprint.safe_print_obj(self.chunks_names)
            breakoint = 1
        utils.print_stop_msg(f"...loading docs via [{self.type_chunking_engine}], created [{len(self.chunks_dicts)}] total chunks from [{fileCount}] files")
        #safeprint.safe_print_obj(self.chunks_dicts,"chunks as a dict")



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
            #top_doc_names   =  [self.chunks_names[i] for i in indices[0]]
            
            start = 0
            stop = len(indices[0])
            for step in range(start, stop):
                i = indices[0][step]
                #doc_name = self.chunks_names[i]
                doc_name = self.chunks_dicts[i]["filename"]
                first_x_last_x_chars = 0
                top_doc_names.append(doc_name)
                distance = utils.dec_pts(distances[0][step],2)
                chunk_summary        = self.chunks_dicts[i]["summary"]#self.chunking_engine.first_x_last_x_chars(self.chunks[i],5)
                chunk_data_len       = self.chunks_dicts[i]["len"]#len(self.chunks[i])
                chunk_offset_in_file = self.chunks_dicts[i]["offsetInFile"]
                print(f"Relevant chunk {step + 1}/{stop}:")
                print(f"  Index:         {i}")
                print(f"  Chunk score:   {distance}")
                print(f"  Chunk source:  {doc_name}")
                print(f"  LocationInFile:{chunk_offset_in_file}")
                #print(f"  Current top_doc_names: {top_doc_names}")
                print(f"  Chunk summary: {chunk_summary}")
                if(self.debug):
                    print(f"  Chunk:         {utils.remove_cr_lf(self.chunks[i])}")
                print()       
                csvStr = f"{self.session_name},{self.type_vector_engine},{self.search_engine_distance_type},{distance},{chunk_data_len},{doc_name},{chunk_offset_in_file}"
                utils.save_csv(AbsRetriever.STATS_SEARCH_HEADER,csvStr,self.stats_file)
            top_chunks = [self.chunks[i] for i in indices[0]]

            reranked_chunks = reretrieve(query_embedding,self.initial_chunk_embeddings,top_chunks)
            #return [self.chunks_names[i] for i in indices[0]]
        #return top_doc_names,top_chunks
        return top_doc_names,reranked_chunks


def reretrieve(query_embedding, original_embeddings, original_top_chunks, top_k=5):
     # Calculate cosine similarity between the query embedding and each retrieved chunk embedding
    similarity_scores = cosine_similarity(query_embedding, np.array(original_embeddings))[0]

    # Pair each chunk with its similarity score
    scored_chunks = list(zip(similarity_scores, original_top_chunks))

    # Sort the chunks by similarity scores in descending order
    reranked_chunks = sorted(scored_chunks, key=lambda x: x[0], reverse=True)[:top_k]

    # Unpack the chunks and their similarity scores
    final_chunks = [chunk for _, chunk in reranked_chunks]
    final_similarities = [score for score, _ in reranked_chunks]

    return final_chunks, final_similarities

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