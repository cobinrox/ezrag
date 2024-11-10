import argparse
import os
import sys
import time
from packages.utils import utils
from packages.utils import remenu
from packages.ragimpls.faissretriever  import Naive_ST_FAISS_Retriever
from packages.ragimpls.simpleretriever import SimpleRetriever
#from packages.ragimpls.whooshretriever import WhooshRetriever
from packages.ragimpls.tinyllmgenerator import TinyLLmGenerator
from packages.ragimpls.t5smallgenerator import T5SmallGenerator
from packages.ragimpls.t5basegenerator  import T5BaseGenerator

from packages.ragimpls.simplechunker  import Simple_Chunker
from packages.ragabs.session          import Session


'''
   ezrag
   This is a program that implements a RAG mechansim.  Please see the README
   file for details.

'''

#DEFAULT_QUESTION = "How many fingers does PJ have?"
#DEFAULT_QUESTION = "Where does PJ live?"
DEFAULT_QUESTION = "What is PJ's wife's name and what kind of animal was she?"

# global parser object and command line args
g_parser = None
g_args   = None

'''
    Set up parser for the project
'''
def set_up_cmd_line_parser():
    global g_args
    global g_parser 
    g_parser = argparse.ArgumentParser(description="Options for the ezrag program")
    
    # Add arguments with default values
    g_parser.add_argument("--retriever_name",  default="Naive_ST_FAISS_Retriever", help="Retriever class name to use (currently there [is only one -[Naive_ST_FAISS_Retriever,SimpleRetriever])")
    g_parser.add_argument("--generator_name",  default="TinyLLmGenerator"        , help="Generator class name to use (currently there are: [TinyLLmGenerator,T5SmallGenerator,T5BaseGenerator])")
    g_parser.add_argument("--chunker_name"  ,  default="Simple_Chunker"          , help="Chunker class name to use (currently there is [Simple_Chunker]) ")
    g_parser.add_argument("--docs_dir"      ,  default="docs/geography"          , help="Documents directory")
    g_parser.add_argument("--chunk_max_num" ,  type=int,default="5"              , help="Maximum number of chunks that the retriever should return")

    g_parser.add_argument("--chunk_size"    ,  type=int,default="512"            , help="Chunking size that the chunker should chunk docs up into")
    g_parser.add_argument("--chunk_dist_scoring", default="EUCLIDIAN"            , help="Type of similarity/distance scoring within vector search engine of the retriever")
    g_parser.add_argument("--tempAsStr"     ,  default="NONE"                    , help="Temperature for generator llm scoring, if any")

    g_parser.add_argument("--debug"       ,  type=lambda x: x.lower() == 'true', default=True, help="Enable debug")
    g_parser.add_argument("--quantize"    ,  type=lambda x: x.lower() == 'true', default=True, help="Quantize")
    g_parser.add_argument("--interactive" ,  type=lambda x: x.lower() == 'true', default=True, help="Keep program open after finishing and run interactively")
    g_parser.add_argument("--question"    ,  default=DEFAULT_QUESTION          , help="Question you want to ask")

'''
    Takes the sys args passed to the program (or updated to sys) and uses the
    program's parser to generate flat g_args array.  WHen finished, the global
    g_args variable will be set with the program's args.
'''
def parse_my_args():
    global g_parser
    global g_args
    # Parse the arguments
    g_args = g_parser.parse_args()
    
    # Convert comma-separated ids to a list of integers
    #g_args.ids = [int(id) for id in g_args.ids.split(',')]
    utils.printf("===== Main input parameters: =====")
    utils.printf(f"retriever name : [{g_args.retriever_name}]"    )
    utils.printf(f"Generator name : [{g_args.generator_name}]"    )
    utils.printf(f"Chunker name   : [{g_args.chunker_name}]"    )
    utils.printf(f"Chunk max num  : [{g_args.chunk_max_num}]"    )
    utils.printf(f"Chunk size     : [{g_args.chunk_size}]"    )
    utils.printf(f"Dist. Scoring  : [{g_args.chunk_dist_scoring}]")
    utils.printf(f"Question       : [{g_args.question}]")

    if(g_args.tempAsStr == "NONE"):
        g_args.temperature = None
    else:
        g_args.temperature = float(g_args.tempAsStr)
    utils.printf(f"Temperature    : [{g_args.temperature}] ({type(g_args.temperature)})")
    utils.printf(f"Documents dir  : [{g_args.docs_dir}]"    )
    utils.printf(f"Quantize       : [{g_args.quantize}]")
    #utils.printf(f"Num Loops  : [{args.num_loops}]")
    utils.printf(f"Debug          : [{g_args.debug}]")
    utils.printf(f"Interactive    : [{g_args.interactive}]")
    #utils.printf(f"IDs        : [{g_args.ids}]")
    utils.printf("===== End Main Input Params ====")
    #return g_args   

'''
    Run a rag session
'''
def run_session():
    # set up session/config obj used by all of the pieces of the RAG
    sessionNumber = int(round(time.time() * 1000))
    session = Session()
    session.session_num = sessionNumber
    session.ses_start_time = int(round(time.time() * 1000))
    session.ses_retriever_type = g_args.retriever_name
    session.ses_generator_type = g_args.generator_name
    session.ses_chunker_name   = g_args.chunker_name
    session.ses_max_top_k_chunks  = g_args.chunk_max_num
    session.ses_chunk_size     = g_args.chunk_size
    session.ses_similarity_score_type = g_args.chunk_dist_scoring
    session.ses_temperature    = g_args.temperature
    session.ses_quantize       = False
    session.ses_question       = g_args.question
    session.ses_debug          = g_args.debug
    #session.ses_embedding_root_dir  = "./EMBEDDINGS"
    
    docs_dir = utils.to_absolute_path(g_args.docs_dir) #os.path.abspath(os.path.join(os.path.dirname(__file__), g_args.docs_dir))
    if not os.path.exists(docs_dir):
        utils.printf(f"Cannot find docs_dir [{docs_dir}], will not be using docs in the RAG search")
    else:
        session.ses_docs_dir = docs_dir


    # Initialize the chunker (right now we only have one kind)
    #if session.ses_chunker_name == "Simple_Chunker":
    chunker = Simple_Chunker(session)
    #else:
    #    pass

    # Initialize the retriever, passing its parameters
    retriever = None
    if( g_args.retriever_name == "Naive_ST_FAISS_Retriever"):
        #retriever = Naive_ST_FAISS_Retriever(docs_dir=docs_dir,chunk_size=g_args.chunk_size,search_engine_similarity_score_type=g_args.chunk_dist_scoring, flush=True)
        retriever = Naive_ST_FAISS_Retriever(session)
    #elif( g_args.retriever_name == "WhooshRetriever"): NOT READY YET
    #    pass
    elif( g_args.retriever_name == "SimpleRetriever"):
        retriever = SimpleRetriever(session)
    
    # initialize the generator
    generator = None
    if( g_args.generator_name == "TinyLLmGenerator"):
        generator = TinyLLmGenerator(session)
    elif (g_args.generator_name == "GPTJGenerator"):
        pass #generator = GPTJGenerator()
    elif (g_args.generator_name == "T5SmallGenerator"):
        generator = T5SmallGenerator(session)
    elif (g_args.generator_name == "T5BaseGenerator"):
        generator = T5BaseGenerator(session)

    # the retriever relies on the chunker, so pass chunker to the retriever
    retriever.injectChunker(chunker)
    
    # ask the retriever to do its job, returning to us the top chunks
    # that it found
    top_doc_names,top_chunks = retriever.public_retrieve_documents(g_args.question)

    # then turn around and ask the genertor to do its job, which is just to
    # take the top chunks from the retriver, and the user's query, and see what
    # comes out
    x = generator.public_generate_response(g_args.question,top_chunks)
    session.ses_end_time = int(round(time.time() * 1000))
    session.ses_answer = x
    utils.printf(f"Question: [{g_args.question}]")
    utils.printf(f"Answer:   [{x}]")
    utils.printf("================")
    utils.printf(f"Sources: {top_doc_names}")
    if(g_args.interactive):
        # if we started in interactive mode, then print out a prompt to
        # allow the user to rate how well they thought the answer was
        rating = utils.get_rating()
        session.ses_rating = rating
    # and write out the session information and results to csv file
    session.write_to_csv()
 
#
#  START UP !
#
if __name__ == "__main__":
    # initialize parser
    set_up_cmd_line_parser()
    while True:
        parse_my_args() # we can loop, so reparse any changes that the user may
                        # have made at the end of loop

        run_session()
        utils.printf(f"CSV files for this session/s can be found at: [./STATS]")

        if(not g_args.interactive):
            utils.printf(f"buh bye")
            sys.exit(0)
        # if running interactively, then let user reset parameters via simple
        # stdin menu
        new_args = remenu.run_menu(g_args,g_parser)
        if(new_args[0] == "x"):
            utils.printf("buh bye")
            sys.exit(0)
        # after getting new user options, reset the system args
        # and go back and loop again
        sys.argv = [sys.argv[0]] + new_args  # Replace command-line arguments

        


