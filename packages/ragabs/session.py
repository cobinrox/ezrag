import os
import time
from utils import utils
'''
   Holder for information relating to a run time session.  Holds config information needed by
   all of the items in the RAG implementation, from chunking settings, to retrieval settings,
   to generator settings, and others.  Can be used to print to a csv string for tracking stats.
'''
class Session:
    # csv string header
    SESSION_CSV_HEADER  = "SessionNum,ExeTime,RetrieverType,GeneratorType,GenTokenSupport,ChunkerType,SimilarityType,MaxTopChunks,ChunkSize,Temperature,Quantize,ApproxScorePct,Rating"

    def __init__(self):
         self.session_num          = int(round(time.time() * 1000))            # unique val to help with csv statistics, keeping sessions individualized
         self.ses_start_time       = int(round(time.time() * 1000))            # start time of processing 
         self.ses_end_time         = int(round(time.time() * 1000))            # end time of processing
         self.ses_retriever_type   =  ""           # type of the retriever/vector engine
         self.ses_generator_type   = -1            # type of the generator/llm engine
         self.ses_chunker_name     = ""            # type of the chunker
         self.ses_chunk_size       = ""            # size of chunks
         self.ses_similarity_score_type = ""       # type of similarity score used by retriever/vector engine
         self.ses_temperature      = None          # temperature setting for generator/llm
         self.ses_quantize         = True          # whether to try to quantize models
         self.ses_approx_score_pct = "0"           # approx score in percent of closest chunk to query
         self.ses_rating          = -1             # rating from 1-5 provided by human
         self.ses_question         = ""            # the question asked in the session
         self.ses_answer           = ""            # the answer given in the session
         self.ses_debug            = True          # whether to print out more info
         self.ses_docs_dir         = None          # directory where corpus of docs resides
         self.ses_embedding_root_dir    = None     # temporary dir for retriever/vector engines that save to disk
         self.ses_max_top_k_chunks = 5             # number of chunks the retriever/vector engine should find 

         self.ses_generator_token_support = 0      # the token size that the generator/llm can support
                                                   # has to be set at run time when initializing llm's tokenizer

         # use absolute dir paths to support running individual classes during testing
         my_script_directory = os.path.dirname(os.path.abspath(__file__))
         relative_stats_path = "../../STATS"
         abs_stats_path = os.path.abspath(os.path.join(my_script_directory, relative_stats_path))
         if not os.path.exists(abs_stats_path):
            os.makedirs(abs_stats_path)
         self.session_stats_file = os.path.join(abs_stats_path, "session_stats.csv") # location of session csv file
         self.chunk_stats_file = os.path.join(abs_stats_path, "chunk_stats.csv")     # location of chunk csv file

         relateve_embeddings_dir = "../../EMBEDDINGS"
         abs_embed_path = os.path.abspath(os.path.join(my_script_directory, relateve_embeddings_dir))
         if not os.path.exists(abs_embed_path):
            os.makedirs(abs_embed_path)
         self.ses_embedding_root_dir = abs_embed_path                               # location of directory that
                                                                                    # can be used by embedder of 
                                                                                    # retriever


    '''
        Write out this session object to csv file to the STATS directory
        @param self Python idiom syntax
    '''
    def write_to_csv(self):
        csvStr = (
                    f"{self.session_num},"
                    f"{self.ses_end_time-self.ses_start_time},"
                    f"{self.ses_retriever_type},"
                    f"{self.ses_generator_type},"
                    f"{self.ses_generator_token_support},"
                    f"{self.ses_chunker_name},"
                    f"{self.ses_similarity_score_type},"
                    f"{self.ses_max_top_k_chunks},"
                    f"{self.ses_chunk_size},"
                    f"{self.ses_temperature},"
                    f"{self.ses_quantize},"
                    f"{self.ses_approx_score_pct},"
                    f"{self.ses_rating}"
                    )
        utils.save_csv(self.SESSION_CSV_HEADER,csvStr,self.session_stats_file)        
        