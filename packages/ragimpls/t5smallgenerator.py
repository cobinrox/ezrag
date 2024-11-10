import os
import sys
import numpy as np
import torch
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import gc

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Add the parent directory to sys.path
sys.path.append(parent_dir)
from utils import utils
from utils import safeprint
from ragabs.absgenerator import AbsGenerator
from ragabs.session import Session

'''
     Generator that uses the T5-smal encoder/decoder LLM.
'''
class T5SmallGenerator(AbsGenerator):
    model_name = 't5-small'
    def __init__(self, session):
        super().__init__(session)
        utils.printf("Initializing generator...")
        start_init_time = utils.get_current_time_ms()      

        self.set_tokenizer(self.model_name)

        # Load and quantize the model
        utils.print_start_msg("Loading model...")
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name, torch_dtype=torch.float32)
        utils.print_stop_msg("... end loading model")

        # WARNING: SKIPPING QUANTIZATION AS IT PRODUCES FALSE ANSWERS
        if(self.session.ses_quantize):
            utils.printf(f"WARNING SKIPPING QUANTIZATION FOR THIS MODEL DUE TO RESULT ISSUES OBSERVED IN TESTING")
            utils.printf(f"YOU CAN OVERRIDE THIS BEHAVIOR BY EDITING THIS FILE!")

            # utils.print_start_msg("Quantizing...")
            # self.model = torch.quantization.quantize_dynamic(
            #     self.model, {torch.nn.Linear}, dtype=torch.qint8
            # )
            # utils.print_stop_msg("... end quantizing")
        
        # Set up the pipeline for text generation
        utils.print_start_msg("Set up llm pipeline...")
        self.llm = pipeline("text2text-generation", model=self.model, tokenizer=self.tokenizer)
        utils.print_stop_msg("... end setting up llm pipeline")

        init_time = utils.get_current_time_ms() - start_init_time
        utils.printf(f"...end initializing generator took [{init_time/1000}] secs")

 
    def public_generate_response(self, query: str, chunks: list) -> str:
        prompt,approx_num_tokens_of_prompt = self.create_prompt(chunks, query)
        max_tokens_to_use = self.session.ses_generator_token_support
        # try to squeeze out less memory usage, eh
        if approx_num_tokens_of_prompt < self.session.ses_generator_token_support and approx_num_tokens_of_prompt + 128 < self.session.ses_generator_token_support:
            max_tokens_to_use = approx_num_tokens_of_prompt + 128
        

        utils.print_start_msg("Invoking llm...")
        temp = self.session.ses_temperature
        utils.printf(f"temperature [{temp}]")
        utils.printf(f"Quantized? [{self.session.ses_quantize}]")
        utils.printf(f"Your tokens/allowed tokens [{max_tokens_to_use}]/[{self.session.ses_generator_token_support}]")

        response = self.llm(
            prompt,
            max_length=512, #??? wtfmax_tokens_to_use, 
            num_return_sequences=1,
            **(dict(do_sample=True, temperature=temp) if temp else {}),
        )[0]['generated_text']
        utils.print_stop_msg("... end invoking llm")

        safeprint.safe_print_obj(response, "llm response")
        if self.session.ses_quantize == False:
            return response.split("Answer:")[1].split("Context:")[0].strip() if "Answer:" in response else response
        else:
            return response.split("Answer:")[1].split("Context:")[0].strip() if "Answer:" in response else response

    def _quantize(self, model):
        pass  # Placeholder if you want to add custom quantization logic later

# Example usage
if __name__ == "__main__":
    utils.printf("Starting...")

    session = Session()
    session.ses_chunk_size     = 512
    #session.ses_similarity_score_type = AbsRetriever.DOT_PRODUCT_DISTANCE
    session.ses_quantize       = False
    session.ses_question = "how many development types does the udl have"

    # group 0: nominal, no quantize
    groupNum = 0
    for i in range(1):
        loopnum = f"{groupNum}/{i}"
        utils.printf(f" LOOP {loopnum}")
        session.ses_quantize = False
        generator = T5SmallGenerator(session )
        question="where does the cat live"
        x = generator.public_generate_response(question,["A cat has four legs.","The cat lives in the capital of furgenstein.","And a dog has four.","The cat lives in the city of blootbart."])
        utils.printf(f"Question: [{question}]")
        utils.printf(f"The answer: [{x}]")
        utils.printf(f"======================END LOOP {loopnum}")
        gc.collect()
    utils.printf(f"******************************* END TEST GROUP {groupNum}")
    
    # group 1: nominal, quantize
    groupNum = groupNum + 1
    for i in range(1):
        loopnum = f"{groupNum}/{i}"
        utils.printf(f" LOOP {loopnum}")
        session.ses_quantize = True
        generator = T5SmallGenerator(session )
        question="where does the cat live"
        x = generator.public_generate_response(question,["A cat has four legs.","The cat lives in the capital of furgenstein.","And a dog has four.","The cat lives in the city of blootbart."])
        utils.printf(f"Question: [{question}]")
        utils.printf(f"The answer: [{x}]")
        utils.printf(f"======================END LOOP {loopnum}")
        gc.collect()
    utils.printf(f"******************************* END TEST GROUP {groupNum}")

    # group 2: nominal, no quantize again
    groupNum = 0
    for i in range(1):
        loopnum = f"{groupNum}/{i}"
        utils.printf(f" LOOP {loopnum}")
        session.ses_quantize = False
        generator = T5SmallGenerator(session )
        question="where does the cat live"
        x = generator.public_generate_response(question,["A cat has four legs.","The cat lives in the capital of furgenstein.","And a dog has four.","The cat lives in the city of blootbart."])
        utils.printf(f"Question: [{question}]")
        utils.printf(f"The answer: [{x}]")
        utils.printf(f"======================END LOOP {loopnum}")
        gc.collect()
    utils.printf(f"******************************* END TEST GROUP {groupNum}")

    # group 3, skip re-initializing
    groupNum = groupNum + 1
    for i in range(1):
        loopnum = f"{groupNum}/{i}"
        utils.printf(f" LOOP {loopnum}")
        #session.ses_quantize = True
        # test with re-use of generator
        #generator = TinyLLmGenerator(session )
        question="where does the cat live"
        x = generator.public_generate_response(question,["A cat has four legs.","The cat lives in the capital of furgenstein.","And a dog has four.","The cat lives in the city of blootbart."])
        utils.printf(f"Question: [{question}]")
        utils.printf(f"The answer: [{x}]")
        utils.printf(f"======================END LOOP {loopnum}")
        gc.collect()

    # group 4, inductive question, no temperature
    groupNum = groupNum + 1
    loopnum = groupNum+1
    utils.printf(f" LOOP {loopnum}")
    session.ses_quantize = True
    generator = T5SmallGenerator(session )
    question="what is the capital of furgenstein"
    x = generator.public_generate_response(question,["A cat has four legs.","The cat lives in the capital of furgenstein.","And a dog has four.","The cat lives in the city of blootbart."])
    utils.printf(f"Question: [{question}]")
    utils.printf(f"The answer: [{x}]")
    utils.printf(f"======================END LOOP {loopnum}")
    gc.collect()

    # group 4, inductive question, low temp
    groupNum = groupNum + 1
    loopnum = groupNum+1
    utils.printf(f" LOOP {loopnum}")
    session.ses_quantize = True
    session.ses_temperature = 0.1
    generator = T5SmallGenerator(session )
    question="what is the capital of furgenstein"
    x = generator.public_generate_response(question,["A cat has four legs.","The cat lives in the capital of furgenstein.","And a dog has four.","The cat lives in the city of blootbart."])
    utils.printf(f"Question: [{question}]")
    utils.printf(f"The answer: [{x}]")
    utils.printf(f"======================END LOOP {loopnum}")
    gc.collect()

    # group 5, inductive question, high temp
    groupNum = groupNum + 1
    loopnum = groupNum+1
    utils.printf(f" LOOP {loopnum}")
    session.ses_quantize = True
    session.ses_temperature = 0.7
    generator = T5SmallGenerator(session )
    question="what is the capital of furgenstein"
    x = generator.public_generate_response(question,["A cat has four legs.","The cat lives in the capital of furgenstein.","And a dog has four.","The cat lives in the city of blootbart."])
    utils.printf(f"Question: [{question}]")
    utils.printf(f"The answer: [{x}]")
    utils.printf(f"======================END LOOP {loopnum}")
    gc.collect()

    # group 6, this is a doozie, test out security docs, warning you need the security
    # docs placed in the docs dir! also notice we rely on other classes to get context info
    groupNum = groupNum + 1
    loopnum = groupNum+1
    utils.printf(f" LOOP {loopnum}")
    from ragabs.session import Session
    from ragimpls.faissretriever import Naive_ST_FAISS_Retriever
    from ragimpls.simplechunker  import Simple_Chunker    
    session.ses_quantize = True
    session.ses_temperature = None
    my_script_directory = os.path.dirname(os.path.abspath(__file__))
    relative_sec_path = "../../docs/security"
    abs_sec_path = os.path.abspath(os.path.join(my_script_directory, relative_sec_path))
    if not os.path.exists(abs_sec_path):
        utils.printf(f"CANNOT FIND SECURITY DOC DIR [{abs_sec_path}]")
        sys.exit(-1)
    session.ses_docs_dir = abs_sec_path
    session.ses_chunk_size     = 512
    session.ses_similarity_score_type = "EUCLIDIAN"

    chunker = Simple_Chunker(session)
    retriever = Naive_ST_FAISS_Retriever(session) 
    retriever.injectChunker(chunker)
    top_doc_names,top_chunks = retriever.public_retrieve_documents(session.ses_question)
    generator = T5SmallGenerator(session )
    question="how many deployment types does the udl have"
    x = generator.public_generate_response(question,top_chunks)
    utils.printf(f"Question: [{question}]")
    utils.printf(f"The answer: [{x}]")
    utils.printf(f"======================END LOOP {loopnum}")
    gc.collect()


