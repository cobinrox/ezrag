import os
import sys
import shutil
from whoosh import index
from whoosh.fields import Schema, TEXT
from whoosh.qparser import QueryParser
from PyPDF2 import PdfReader  # For processing PDFs
from whoosh.analysis import StemmingAnalyzer
from whoosh.fields import TEXT
#from absretriever import AbsRetriever
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Add the parent directory to sys.path
sys.path.append(parent_dir)
from ragabs.absretriever import AbsRetriever
from ragabs.session import Session
from utils import utils

utils.printf('woot')

# Implement the Retriever using Whoosh
class WhooshRetriever(AbsRetriever):
    def __init__(self, session):
        super().__init__(session)
        self.vector_engine = index
        self.persistent_embeddings_path = self.session.ses_embedding_root_dir + "/whoosh" #"./EMBEDDINGS/whoosh" #persistent_embeddings_path  # Path to store/load the embeddings
        # utils.printf("Checking if whoosh idx dir exists")
        if not os.path.exists(self.persistent_embeddings_path):
            utils.printf("whoosh dir does not exist, so creating")
            os.mkdir(self.persistent_embeddings_path)
            #
        else:
            utils.printf("whoosh idx dir exists")
        # TODO: move out of init
        utils.print_start_msg('creating and populating idx...')    
        self._create_doc_embeddings()
        utils.print_stop_msg('...creating and populating idx')

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

 
    def _create_doc_embeddings(self):
        utils.print_start_msg('creating and populating idx...')    
        #os.mkdir(self.persistent_embeddings_path)
        
        self.schema = Schema(title=TEXT(stored=True), content=TEXT(analyzer=StemmingAnalyzer()))

        ix = self.vector_engine.create_in(self.persistent_embeddings_path, self.schema)
        utils.print_stop_msg('...creating and populating idx')    


        writer = ix.writer()

        # Iterate over all files in the directory
        for filename in os.listdir(self.session.ses_docs_dir):
            filepath = os.path.join(self.session.ses_docs_dir, filename)
            utils.printf(f"Filename [{filename}] Filepath [{filepath}]...")
            # Process text files
            if filename.endswith(".txt"):
                with open(filepath, 'r', encoding='utf-8') as file:
                    utils.print_start_msg(f"reading txt file ...")
                    content = file.read()
                    utils.print_stop_msg("...read txt file")
            # Process PDF files
            elif filename.endswith(".pdf"):
                utils.print_start_msg(f"reading pdf file ...")
                content = self._extract_pdf_text(filepath)
                utils.print_stop_msg("...read pdf file")

            else:
                # Skip non-txt or non-pdf files
                utils.printf("skipping file")
                continue

            # Add document to the index
            utils.print_start_msg("adding file to index...")
            writer.add_document(title=filename, content=content)
            utils.print_stop_msg("...adding file to index")
        utils.printf("persisting embeddings")
        writer.commit()

    def _extract_pdf_text(self, filepath: str) -> str:
        """
        Private method to extract text from a PDF file.
        Input: PDF file path (str)
        Output: Extracted text (str)
        """
        reader = PdfReader(filepath)
        text = ""

        # Extract text from all pages
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()  # Extract text from each page

        return text


    def public_retrieve_documents(self, query: str) -> list:

        ix = self.vector_engine.open_dir(self.persistent_embeddings_path)
        qp = QueryParser("content", schema=self.schema)

        # Parse and execute the query
        q = qp.parse(query)
        with ix.searcher() as searcher:
            utils.print_start_msg("running search...")
            results = searcher.search(q, limit=self.session.ses_max_top_k_chunks)  
            matching_docs = [result['title'] for result in results]
            utils.print_stop_msg("...running search")
        utils.printf(f"found [{matching_docs}] docs")
        return matching_docs
    def _persisted_embeddings_exist(self):
          return os.path.exists(self.persistent_embeddings_path)

# Example usage
if __name__ == "__main__":
    import time

    session = Session()
    session.session_num = int(round(time.time() * 1000))
    session.ses_start_time = int(round(time.time() * 1000))
    session.ses_retriever_type = "whoosh"
    #session.ses_generator_type = g_args.generator_name
    #session.ses_chunker_name   = g_args.chunker_name
    session.ses_chunk_size     = 512
    session.ses_similarity_score_type = AbsRetriever.EUCLIDIAN_DISTANCE
    session.ses_temperature    = None
    session.ses_quantize       = True
    #session.ses_question       = "what is PJ's wife's name"
    session.ses_question       = "how many fingers does PJ have"

    session.ses_debug          = True
    session.ses_embedding_root_dir  = "../../EMBEDDINGS" 
    session.ses_docs_dir       = "../../docs/geography"   

    # Initialize the retriever, passing its parameters
    retriever = WhooshRetriever(session)

    retrieved_docs = retriever.public_retrieve_documents(session.ses_question)

    # Output the results
    print("Retrieved Documents:", retrieved_docs)
