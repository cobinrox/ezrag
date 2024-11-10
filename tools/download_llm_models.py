# you can use this mini program to download models from hugging face
import psutil
import os

memUsage = f"{psutil.Process().memory_info().rss / (1024*1024):.2f} MB"
print(f"[{memUsage}] Prepping to download...",flush=True)
hg_hub_dir = os.path.join(os.path.expanduser("~"), ".cache", "huggingface", "hub")
if(os.path.exists(hg_hub_dir)):
    print(f"Assumming model files will download to: [{hg_hub_dir}]",flush=True)
else:
    print(f"Default model download directory [{hg_hub_dir}] does not exist (yet)",flush=True)

import sys
import gc
from transformers import AutoTokenizer, AutoModelForCausalLM,AutoModelForSeq2SeqLM
from sentence_transformers import SentenceTransformer

#
# this model is used for creating embeddings
#
model_name = 'all-MiniLM-L6-v2'
print(f">>>>>>>>>>[{memUsage}] Downloading [{model_name}]",flush=True)
model = SentenceTransformer(model_name)
gc.collect()
print(f"[{hg_hub_dir}] conents: [{os.listdir(hg_hub_dir)}]",flush=True)
print(f"<<<<<<<<<<[{memUsage}] Downloaded [{model_name}]\n\n",flush=True)

#
# uses as encoder/decoder generator
#
model_name = 't5-base'
print(f">>>>>>>>>>[{memUsage}] Downloading [{model_name}]",flush=True)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
gc.collect()
print(f"[{hg_hub_dir}] conents: [{os.listdir(hg_hub_dir)}]",flush=True)
print(f"<<<<<<<<<<[{memUsage}] Downloaded [{model_name}]\n\n",flush=True)

#
# uses as encoder/decoder generator
#
model_name = 't5-small'
print(f">>>>>>>>>>[{memUsage}] Downloading [{model_name}]",flush=True)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
gc.collect()
print(f"[{hg_hub_dir}] conents: [{os.listdir(hg_hub_dir)}]",flush=True)
print(f"<<<<<<<<<<[{memUsage}] Downloaded [{model_name}]\n\n",flush=True)


#
# used as a chat-based LLM generator
#
model_name = 'TinyLlama/TinyLlama-1.1B-Chat-v1.0'
print(f">>>>>>>>>>[{memUsage}] Downloading [{model_name}]",flush=True)
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
gc.collect()
print(f"[{hg_hub_dir}] conents: [{os.listdir(hg_hub_dir)}]",flush=True)
print(f"<<<<<<<<<<[{memUsage}] Downloaded [{model_name}]",flush=True)

