import argparse
import os
import subprocess
import sys
from packages.utils import utils
from packages.ragimpls.faissretriever import Naive_ST_FAISS_Retriever
#from packages.ragimpls.whooshretriever import WhooshRetriever
from packages.ragimpls.tinyllm        import TinyLLmGenerator

g_args = None

utils.check_venv(True)

def parse_my_args():
    global g_args
    parser = argparse.ArgumentParser(description="Your program description")
    
    # Add arguments with default values
    parser.add_argument("--retreiver_name",  default="Naive_ST_FAISS_Retriever", help="RX name")
    parser.add_argument("--generator_name",  default="TinyLLmGenerator"        , help="GX name")
    parser.add_argument("--docs_dir"      ,  default="./docs/geography"                 , help="Documents directory")
    parser.add_argument("--chunk_size"    ,  type=int,default="512"            , help="Nominal chunking size")

    #parser.add_argument("--quantize"      ,  action="store_true"               , help="Whether to quantize")#default="true"                       )
    #parser.add_argument("--num_loops",     type=int,default="1",        help="Number of times to run query")
    #parser.add_argument("--debug"         ,  action="store_true"               , help="Use debugg")
    parser.add_argument("--debug"          ,  type=lambda x: x.lower() == 'true', default=True, help="Enable debug")
    parser.add_argument("--quantize"          ,  type=lambda x: x.lower() == 'true', default=True, help="Quantize")

    #parser.add_argument("--ids"  ,    default="1", help="IDs (comma-separated)")
    
    # Parse the arguments
    g_args = parser.parse_args()
    
    # Convert comma-separated ids to a list of integers
    #g_args.ids = [int(id) for id in g_args.ids.split(',')]
    utils.printf("===== Main input parameters: =====")
    utils.printf(f"Retreiver name : [{g_args.retreiver_name}]"    )#+str(type(args.retreiver_name)))
    utils.printf(f"Generator name : [{g_args.generator_name}]"    )#+str(type(args.generator_name)))
    utils.printf(f"Documents dir  : [{g_args.docs_dir}]"    )#+str(type(args.docs_dir)))

    utils.printf(f"Chunk size     : [{g_args.chunk_size}]" )#+ str(type(args.chunk_size)))
    utils.printf(f"Quantize       : [{g_args.quantize}]")
    #utils.printf(f"Num Loops  : [{args.num_loops}]")

    utils.printf(f"Debug          : [{g_args.debug}]")
    #utils.printf(f"IDs        : [{g_args.ids}]")
    utils.printf("===== End Main Input Params ====")
    #return g_args   

 
#
#  START UP !
#
if __name__ == "__main__":
    #global g_args
    parse_my_args()
    # Your main program code here
    # The question we want to ask
    thequestion = "What is PJ's wife's name and what kind of animal was she?"
    docs_dir = utils.to_absolute_path(g_args.docs_dir) #os.path.abspath(os.path.join(os.path.dirname(__file__), g_args.docs_dir))
    if not os.path.exists(docs_dir):
        utils.printf(f"Cannot find docs_dir [{docs_dir}], will not be using docs in the RAG search")

    # Initialize the retriever, passing its parameters
    retriever = Naive_ST_FAISS_Retriever(docs_dir=docs_dir,chunk_size=512,flush=True)
    #retriever = WhooshRetriever(docs_dir=docs_directory,chunk_size=0,flush=True)
    generator = TinyLLmGenerator()

       # Query
    top_doc_names,top_chunks = retriever.public_retrieve_documents(thequestion, top_k=5)

    #print("Top retrieved documents:", top_doc_names)
    #print("Top chunks :", top_chunks)

    x = generator.generate_response(thequestion,top_chunks)
    utils.printf("Question: " + thequestion)
    utils.printf("Answer:")
    utils.printf(x)
    utils.printf("================")
