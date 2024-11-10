import os
import fitz
import sys
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Add the parent directory to sys.path
sys.path.append(parent_dir)

from ragabs.chunk import Chunk
from ragabs.abschunker import AbsChunker
from ragabs.session import Session
from utils import utils
from utils import safeprint

'''
    Simple naieve chunker, just chunks up docs based on number of chars.
    Only handles txt and pdf files.
'''
class Simple_Chunker(AbsChunker):
    def __init__(self, session):
        super().__init__(session)

    def public_chunk_the_docs(self):
        fileCount = 0
        total_chunk_idx = 0
        utils.print_start_msg(f"loading and chunking docs ...")
        for filename in os.listdir(self.session.ses_docs_dir):
            fileCount = fileCount + 1
            filepath = os.path.join(self.session.ses_docs_dir, filename)

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
            local_chunk_offset_in_this_file = 0

            for a_local_chunk in local_chunks:
                a_chunk_obj = Chunk()
                a_chunk_obj.chk_name= f"chunk_{total_chunk_idx}"  #f"chunk_{len(self.chunk_dicts)}"
                a_chunk_obj.chk_idx= total_chunk_idx # len(self.chunk_dicts)
                    #"value"        : a_local_chunk
                a_chunk_obj.chk_summary= utils.first_x_last_x_chars(a_local_chunk,3)
                a_chunk_obj.chk_len= len(a_local_chunk)
                a_chunk_obj.chk_filename= filename
                a_chunk_obj.chk_offsetInFile= local_chunk_offset_in_this_file
                a_chunk_obj.chk_dummy= "whatever"
                #a_chunk_obj.chk_similarity_score_type = 
                a_chunk_obj.chk_initial_score=  -1
                a_chunk_obj.chk_reretrieved_score= -1
                a_chunk_obj.chk_embedding= None  
                a_chunk_obj.chk_size = self.session.ses_chunk_size
                 
                self.chunk_objs.append( a_chunk_obj)

                local_chunk_offset_in_this_file = local_chunk_offset_in_this_file + len(a_local_chunk)
                total_chunk_idx = total_chunk_idx+1
            #safeprint.safe_print_obj(self.chunks)
            #safeprint.safe_print_obj(self.chunks_names)
        utils.print_stop_msg(f"...loading docs, created [{len(self.chunk_objs)}] total chunks from [{fileCount}] files")
        #safeprint.safe_print_obj(self.chunk_dicts,"chunks as a dict")

    def _extract_pdf_text(self, filepath: str) -> str:
        doc = fitz.open(filepath)
        text = ""
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            text += page.get_text()
        doc.close()
        return text
    def _chunk_text(self, text: str) -> list:
        # Split the text into chunks of self.chunk_size characters
        return [text[i:i + self.session.ses_chunk_size] for i in range(0, len(text), self.session.ses_chunk_size)]
    
# Example usage

if __name__ == "__main__":
    docs_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'docs/geography'))
    session = Session()
    session.ses_chunk_size     = 512
    
    # need to set this absolutely if running in debugger
    my_script_directory = os.path.dirname(os.path.abspath(__file__))
    relative_sec_path = "../../docs/geography"
    abs_sec_path = os.path.abspath(os.path.join(my_script_directory, relative_sec_path))
    if not os.path.exists(abs_sec_path):
        utils.printf(f"CANNOT FIND  DOC DIR [{abs_sec_path}]")
        sys.exit(-1)
    session.ses_docs_dir = abs_sec_path

    utils.printf(" LOOP 1")
    chunker = Simple_Chunker(session)
    chunker.public_chunk_the_docs()
    the_chunk_objs = chunker.chunk_objs
    for a_chunk_obj in chunker.chunk_objs:
        safeprint.safe_print_obj(a_chunk_obj, "chunk")
 
       

