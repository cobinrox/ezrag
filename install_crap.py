# use this to install various ai dependencies into your venv until we
# get a working legit requirements.txt that actually works with pip
# eye roll
import argparse
import os
import subprocess
import sys
from packages.utils import utils
g_args = None

# first tell user whether or not they are running in a venv,
# if they are not then force them to continue anyway or quit,
# if they choose to quit, then good, the utils will quit. We
# really don't want to be running a bunch of installations outside
# of a venv since python is notorious for getting libs and versions
# tangled up, so this is just a stop-gap/check point to let user know
# if s/he's running in a venv.
utils.check_venv(True)

# List of required modules (to be imported):packages (that must be pip installed)
required_libraries = {
    "transformers"                        : ["transformers"],
    "torch"                               : ["torch"],
    "faiss"                               : ["faiss-cpu"],
    "numpy"                               : ["numpy"],
    "sentence_transformers"               : ["sentence-transformers"],

    "PyPDF2"                              : ["PyPDF2"],
    "langchain_community.document_loaders": ["langchain_community","pypdf"],
    'whoosh'                              : ["whoosh"],
    "fitz"                                : ["PyMuPDF"]
}

# run a util to check if the required libs are already installed in our
# environment and, if not, try to go out and install them
utils.check_and_install_packages(required_libraries)

# next, now try to actually import them as if this were a legit
# python script that needs to import them, if the above install
# worked, then these imports should work too
utils.printf("trying actual imports now...")
try:
    import torch
    from transformers import GPT2LMHeadModel, GPT2Tokenizer
    from sentence_transformers import SentenceTransformer
    import faiss
    import numpy as np
    from PyPDF2 import PdfReader
    from langchain_community.document_loaders import PyPDFLoader
    import fitz
    utils.printf("actual imports completed")
except Exception as e:
    utils.printf(f"ERROR STILL CANNOT IMPORT STUFF: {e}")
    sys.exit(-1)

 
#
#  START UP !
#
if __name__ == "__main__":
    print("Installer complete.  I think",flush=True)