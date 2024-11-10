import os
import sys
import operator
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import faiss
import numpy as np
import torch
from sentence_transformers import SentenceTransformer

# nasty syntax to allow access to packages from various sub dirs
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Add the parent directory to sys.path
sys.path.append(parent_dir)
from utils import utils
from utils import safeprint
from ragabs.absretriever import AbsRetriever
from ragimpls.faisscosine import Faiss_Cosine
from ragabs.session import Session

# more nasty syntax to allow vscode to run this file in python debugger
#sys.path.append('../utils')


'''
    A retriever implementation that uses the facebook FAISS as a vector/search
    engine and the mini-LLM as its embedder/encoder.  The caller can inject (set)
    any valid implementation of the AbsChunker class (ok, currently all we have
    is the simple chunker, but eh)
'''
class Naive_ST_FAISS_Retriever(AbsRetriever):
    embedding_model_name: str = 'all-MiniLM-L6-v2'            

    def __init__(self, session):
        super().__init__(session)
        utils.printf("Initializing retriever ...")
        if( self.session.ses_docs_dir):
            if not os.path.exists(self.session.ses_docs_dir):
                utils.printf(f"Warning doc dir [{self.session.ses_docs_dir}] not found.")
                self.session.ses_docs_dir = None

        # testing- importing sometimes takes too long, so wanted to try lazy loading
        # utils.print_start_msg("importing SentenceTransformer")
        # from sentence_transformers import SentenceTransformer
        # utils.print_stop_msg("imported Sentencetransformer")

        utils.print_start_msg("Loading, quantizing embedding model...")
        self.embedding_engine_model = SentenceTransformer(self.embedding_model_name)
        if(self.session.ses_quantize):
            self.embedding_engine_model = torch.quantization.quantize_dynamic(
                self.embedding_engine_model,
                {torch.nn.Linear},  # Specify the layers to be quantized
                dtype=torch.qint8   # Use 8-bit integer quantization
            )
        utils.print_stop_msg("... end loading embedding model")

        self.vector_engine = None
        #No- doesnt work when running from root:self.persistent_embeddings_path = "../../EMBEDDINGS"#persistent_embeddings_path  # Path to store/load the FAISS index
        self.persistent_embeddings_path = self.session.ses_embedding_root_dir + "/faiss/faiss" + "_" + str(self.session.session_num)
        utils.ensure_directory_exists(self.persistent_embeddings_path)
        utils.printf(f"data dir [{os.path.abspath(self.persistent_embeddings_path)}] exists? {os.path.exists(os.path.abspath(self.persistent_embeddings_path))}]")
        #self.initial_chunk_embeddings = None

        utils.printf("...end initializing retriever")
   

    def _create_doc_embeddings(self):
        # todo: by-pass re chunking and embedding if flag is set
        # if( len(self.chunker.chunks) > 0 ):
        #     utils.printf(f"There are already [{len(self.chunker.chunks)}] chunks embedded, skipping this step")
        #     return
        
        # chunker does the work, then keeps an array of the chunks and an array
        # of chunk_objs that descibe the chunks
        self.chunker.public_chunk_the_docs()

        if len(self.chunker.chunk_objs) == 0:
            print("FYI- No documents to index.")

        # Convert the document chunks to embeddings
        utils.print_start_msg(f"embedding/encoding chunks...")
        #safeprint.safe_print_obj(self.embedding_engine_model,"embedder engine")
        embeddings = self.embedding_engine_model.encode(self.chunker.chunks, show_progress_bar=False)
        ei = 0
        for emb in embeddings:
            self.chunker.chunk_objs[ei].chk_embedding  = emb
            ei = ei + 1

        utils.print_stop_msg(f"...embedding/encoding chunks")
        #safeprint.safe_print_obj(embeddings,"embeddings")

        # Create a Faiss searcher
        utils.print_start_msg(f"creating embedding store...")
        if(self.session.ses_similarity_score_type == AbsRetriever.EUCLIDIAN_DISTANCE):
            self.vector_engine = faiss.IndexFlatL2(embeddings.shape[1])
        elif self.session.ses_similarity_score_type == AbsRetriever.DOT_PRODUCT_DISTANCE:
            self.vector_engine = faiss.IndexFlatIP(embeddings.shape[1])
        #warning: cosine searcher not fully implemented
        elif self.session.ses_similarity_score_type == AbsRetriever.COSINE_DISTANCE:
            self.vector_engine = Faiss_Cosine(embeddings.shape[1])
        utils.print_stop_msg(f"...creating embedding store")
        
        # Add the embeddings to the search db
        utils.print_start_msg(f"adding embeddings to embedding store...")
        self.vector_engine.add(embeddings)
        utils.print_stop_msg(f"...adding embeddings to embedding store")
        # now stored with the chunk_objs: self.initial_chunk_embeddings = embeddings
        # Persist the embeddings to disk todo: is this necessary?
        utils.print_start_msg(f"saving embeddings to disk as file [{self.persistent_embeddings_path}]]...")
        faiss.write_index(self.vector_engine, self.persistent_embeddings_path)
        utils.print_stop_msg(f"...saving embeddings to disk ")


    def public_retrieve_documents(self, query: str) -> list:
        top_chunk_objs = []
        if(self.session.ses_docs_dir is not None):
            self._create_doc_embeddings()
    
            # Convert the user's query into a vector
            query_embedding = self.embedding_engine_model.encode([query])
            
            # Search the embeddings store for the nearest documents to the user's query
            utils.print_start_msg(f"querying embeddings for max [{self.session.ses_max_top_k_chunks}] ...")
            distances, indices = self.vector_engine.search(query_embedding, self.session.ses_max_top_k_chunks)
            print(type(distances))
            max_initial_score = float(distances.max())
            safeprint.safe_print_obj(distances, "search result distances")
            safeprint.safe_print_obj(indices, "search result indices")
            utils.print_stop_msg("...querying embeddings")
            
            # update the chunks that we found/w the new similarity scores
            start = 0
            stop = len(indices[0])
            for step in range(start, stop):
                i = indices[0][step]
                doc_name = self.chunker.chunk_objs[i].chk_filename
                distance = utils.dec_pts(distances[0][step],2)
                self.chunker.chunk_objs[i].chk_similarity_score_type = self.session.ses_similarity_score_type
                self.chunker.chunk_objs[i].chk_initial_score  = distance
                #self.chunker.chunk_objs[i].chk_approx_percent_score = self.approx_percent_score(str(distance),
                #                                                                              self.chunker.chunk_objs[i].chk_similarity_score_type,
                #                                                                                max_initial_score  )
                # debug print this info out, tis handy
                print(f"Relevant chunk {step + 1}/{stop}:")
                print(f"  Index:         {i}") #/{self.chunker.chunk_objs[i].chk_idx}") # should be same value
                print(f"  Chunk score:   {self.chunker.chunk_objs[i].chk_initial_score} ({self.chunker.chunk_objs[i].chk_approx_percent_score})")
                print(f"  Chunk source:  {doc_name}")#/{self.chunker.chunk_objs[i].chk_filename}") # should be same value
                print(f"  LocationInFile:{self.chunker.chunk_objs[i].chk_offsetInFile}")
                print(f"  Chunk summary: {self.chunker.chunk_objs[i].chk_summary}")
                if(self.session.ses_debug):
                    print(f"  Chunk:         {utils.remove_cr_lf(self.chunker.chunks[i])}")
                print()       
            top_chunk_objs = [self.chunker.chunk_objs[i] for i in indices[0]]

            # do a re-retrieval
            reranked_chunks = self._reretrieveEm(query_embedding,top_chunk_objs)[0]

            # save off the chunk info to csv
            for chunk_dict in top_chunk_objs:
                csvStr = (
                            f"{self.session.session_num},"
                            f"{self.session.ses_retriever_type},"
                            #f"{self.generator.getTemperature() or 0}," temp does not affect retrieval
                            f"{chunk_dict.chk_similarity_score_type},"
                            f"{chunk_dict.chk_initial_score},"
                            'COSINE,' # reretrieval scoring type
                            f"{chunk_dict.chk_reretrieved_score},"
                            f"{chunk_dict.chk_approx_percent_score},"
                            f"{chunk_dict.chk_len},"
                            f"{chunk_dict.chk_filename},"
                            f"{chunk_dict.chk_offsetInFile}"
                          )
                utils.save_csv(AbsRetriever.CHUNK_STATS_CSV_HEADER,csvStr,self.session.chunk_stats_file)
        top_doc_names = []
        top_chunks    = []
        # create array of top-doc-names as strings and top_chunks as array of the chunks
        for a_chk_obj in top_chunk_objs:
            # make the top-doc-names include the name of the file, the offset within the file, the
            # approx initial search score as percent, and the aprrox re-retrieval score as percent
            top_doc_names.append(
                f"{a_chk_obj.chk_filename} "
                f"({a_chk_obj.chk_offsetInFile}/"
                #f"{self.approx_percent_score(a_chk_obj.chk_initial_score,    self.session.ses_similarity_score_type, max_initial_score)}/"
                f"{utils.dec_pts(a_chk_obj.chk_approx_percent_score,2)}%)" # currently reretriever is COSINE only
                #f"{self.approx_percent_score(a_chk_obj.chk_reretrieved_score, "COSINE")})" # currently reretriever is COSINE only
            )
            # then just fill out the chunk
            top_chunks.append(self.chunker.chunks[a_chk_obj.chk_idx])  

        # mark the session's highest approx percentage search score to help with stats
        if( len(top_chunk_objs) > 0):
            self.session.ses_approx_score_pct = top_chunk_objs[0].chk_approx_percent_score
        return top_doc_names,top_chunks

    '''
        Run a re-retrieval since that is the big thing of the week.
        Doesn't really help with rescoring though
        @param self Python sytax for classes
        @param query_embedding the embedding value of the original query
        @param top_chunk_objs an array of the chunk objects that were a result of the oringal similarity search
        Side effect: updates the top_chunk_objects with reretrieval score and resorts them based on re-retrieval
        scores
    '''
    def _reretrieveEm(self,query_embedding, top_chunk_objs):
        # Re-Calculate cosine similarity between the query embedding and each retrieved chunk embedding
        top_chunk_embeddings = []
        for a_chunk_obj in top_chunk_objs:
            top_chunk_embeddings.append(a_chunk_obj.chk_embedding)
        new_score_array = cosine_similarity(query_embedding, np.array(top_chunk_embeddings))[0]
        utils.printf(f"new score array {new_score_array}")
        new_max_score = new_score_array.max()
        new_percentages = utils.convert_cosine_similarity_to_percentage(new_score_array)
        # update the dicts' re-retrieve scores, this helps us with statistic checking
        dict_num = 0
        for a_chunk_obj in top_chunk_objs:
            self.chunker.chunk_objs[a_chunk_obj.chk_idx].chk_reretrieved_score = utils.dec_pts(new_score_array[dict_num],2)
            self.chunker.chunk_objs[a_chunk_obj.chk_idx].chk_approx_percent_score = new_percentages[dict_num]


            #self.chunker.chunk_objs[a_chunk_obj.chk_idx].chk_approx_percent_score = self.approx_percent_score(self.chunker.chunk_objs[a_chunk_obj.chk_idx].chk_reretrieved_score,
            #                                                                                                  'COSINE',new_max_score)
            dict_num = dict_num+1

        # re-sort the top_chunk_objs array per the new re-retrieved score values
        top_chunk_objs.sort(key=operator.attrgetter('chk_reretrieved_score'), reverse=True)
        return top_chunk_objs


# Example usage

if __name__ == "__main__":
    utils.printf("Starting...")
    import time
    from ragimpls.simplechunker  import Simple_Chunker

    session = Session()
    session.ses_chunk_size     = 512
    session.ses_similarity_score_type = AbsRetriever.EUCLIDIAN_DISTANCE
    session.ses_quantize       = False
    session.ses_question       = "what is PJ's wife's name"
    #session.ses_question       = "how many fingers does PJ have"
    #session.ses_question = "how many development types does the udl have"

    session.ses_debug          = False
    #session.ses_embedding_root_dir  = "../../EMBEDDINGS" 
    session.ses_docs_dir       = "../../docs/geography" 
    #session.ses_docs_dir       = "../../docs/security" 

    utils.printf(" LOOP 1")
    chunker = Simple_Chunker(session)
    retriever = Naive_ST_FAISS_Retriever(session) 
    retriever.injectChunker(chunker)
    top_doc_names,top_chunks = retriever.public_retrieve_documents(session.ses_question)

    print("Top retrieved documents:", top_doc_names)
    print("Top chunks :", top_chunks)
    utils.printf(" ==================================== END LOOP 1")

    # this test proves that reretrieval is useless, the orignal
    utils.printf(" ")
    utils.printf(" LOOP 2")
    session.session_num = int(round(time.time() * 1000))
    session.ses_quantize = True
    session.ses_question = "what type of shirt did pj wear proudly"

    # need to set this absolutely if running in debugger
    my_script_directory = os.path.dirname(os.path.abspath(__file__))
    relative_sec_path = "../../docs/geography"
    abs_sec_path = os.path.abspath(os.path.join(my_script_directory, relative_sec_path))
    if not os.path.exists(abs_sec_path):
        utils.printf(f"CANNOT FIND  DOC DIR [{abs_sec_path}]")
        sys.exit(-1)
    session.ses_docs_dir = abs_sec_path
 

    chunker = Simple_Chunker(session)
    retriever = Naive_ST_FAISS_Retriever(session) 
    retriever.injectChunker(chunker)
    top_doc_names,top_chunks = retriever.public_retrieve_documents(session.ses_question)

    print("Top retrieved documents:", top_doc_names)
    print("Top chunks :", top_chunks)
    utils.printf(" END LOOP 2")



