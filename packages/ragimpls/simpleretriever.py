import os
import sys
import operator

# nasty syntax to allow access to packages from various sub dirs
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Add the parent directory to sys.path
sys.path.append(parent_dir)
from ragabs.absretriever import AbsRetriever
from utils import utils
from ragabs.session import Session

'''
    Simple retriever that uses a percentage of found words as its search algorithm.
    Doesn't use a vector store or vector search, just a stupid simple string search.
    Can be used for testing or just understanding how a rag search works.
'''
class SimpleRetriever(AbsRetriever):
    def __init__(self, session):
        super().__init__(session)
        utils.printf("Initializing retriever ...")

    def _create_doc_embeddings(self):
        self.chunker.public_chunk_the_docs()

    def _percentage_words_found(self, main_string, search_string):
        # Convert both strings to lowercase for case-insensitive comparison
        main_string = main_string.lower()
        search_string = search_string.lower()

        # Split both strings into words
        main_words = main_string.split()
        search_words = search_string.split()

        # Count the number of words found
        words_found = sum(1 for word in search_words if word in main_words)

        # Calculate the percentage
        total_words_in_main = len(main_words)
        if total_words_in_main == 0:
            return 0  # Avoid division by zero

        percentage = (words_found / total_words_in_main) * 100

        return round(percentage, 2)  # Round to 2 decimal places
    def public_retrieve_documents(self, query: str) -> list:
        self._create_doc_embeddings()
        top_doc_names = []
        top_chunks    = []
        # create array of top-doc-names as strings and top_chunks as array of the chunks
        i = 0
        for a_chk_obj in self.chunker.chunk_objs:
            simscore =self._percentage_words_found(self.chunker.chunks[i],query)
            if(simscore >= 0):
                a_chk_obj.chk_initial_score = simscore
                a_chk_obj.chk_similarity_score_type = self.session.ses_similarity_score_type
                a_chk_obj.chk_approx_percent_score  = simscore
                #top_chunks.append( a_chk_obj)
                i = i +1

        # re-sort the chunk_objs array per the score values
        self.chunker.chunk_objs.sort(key=operator.attrgetter('chk_approx_percent_score'), reverse=True)
            
        i = 1
        for a_chk_obj in self.chunker.chunk_objs:
            top_chunks.append(self.chunker.chunks[a_chk_obj.chk_idx])
            top_doc_names.append(
                f"{a_chk_obj.chk_filename} "
                f"({a_chk_obj.chk_offsetInFile}/"
                f"{a_chk_obj.chk_approx_percent_score}%)"
            )
            csvStr = (
                f"{self.session.session_num},"
                f"{self.session.ses_retriever_type},"
                #f"{self.generator.getTemperature() or 0}," temp does not affect retrieval
                f"{a_chk_obj.chk_similarity_score_type},"
                f"{a_chk_obj.chk_initial_score},"
                'NONE,' # reretrieval scoring type
                f"{a_chk_obj.chk_reretrieved_score},"
                f"{a_chk_obj.chk_approx_percent_score},"
                f"{a_chk_obj.chk_len},"
                f"{a_chk_obj.chk_filename},"
                f"{a_chk_obj.chk_offsetInFile}"
                )
            utils.save_csv(AbsRetriever.CHUNK_STATS_CSV_HEADER,csvStr,self.session.chunk_stats_file)
            if i == session.ses_max_top_k_chunks:
                break
            i = i+1
        return top_doc_names,top_chunks

# Example usage

if __name__ == "__main__":
    utils.printf("Starting...")
    import time
    from ragimpls.simplechunker  import Simple_Chunker

    session = Session()
    session.ses_chunk_size     = 512
    session.ses_retriever_type = "SimpleRetriever"
    session.ses_similarity_score_type = "STRING_COMPARE"
    session.ses_question       = "oh yeah you wish"

    my_script_directory = os.path.dirname(os.path.abspath(__file__))
    relative_sec_path = "../../docs/geography"
    abs_sec_path = os.path.abspath(os.path.join(my_script_directory, relative_sec_path))
    if not os.path.exists(abs_sec_path):
        utils.printf(f"CANNOT FIND  DOC DIR [{abs_sec_path}]")
        sys.exit(-1)
    session.ses_docs_dir = abs_sec_path


    utils.printf(" LOOP 1")
    chunker = Simple_Chunker(session)
    retriever = SimpleRetriever(session) 
    retriever.injectChunker(chunker)
    top_doc_names,top_chunks = retriever.public_retrieve_documents(session.ses_question)

    print("Top retrieved documents:", top_doc_names)
    print("Top chunks :", top_chunks)
    utils.printf(" ==================================== END LOOP 1")
