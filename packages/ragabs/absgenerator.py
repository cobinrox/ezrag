import os
import sys
from abc import ABC, abstractmethod
from transformers import AutoTokenizer

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Add the parent directory to sys.path
sys.path.append(parent_dir)
from utils import utils

'''
    Abstract class for a generator.  A generator relies on a retriever to provide a list of
    data chunks, and an llm to run the final query of the user.
'''
class AbsGenerator(ABC):

    '''
        Constructor.
        @param self Python idiom required for syntax.
        @param session contains configuration information such as the location of the docs to query,
                       and stats/results information
    '''
    def __init__(self,session):
        self.session = session

    '''
        Common utility method to set up a tokenizer, also provides handy mechanism to grab
        and save off the max tokens the llm supports, that info is handy to update in the sessoin
        object to help with stats.
        @param self Python idiom needed for syntax
        @param model_path_or_name name of or path to the llm model
    '''
    def set_tokenizer(self,model_path_or_name):
        self.tokenizer = AutoTokenizer.from_pretrained(model_path_or_name)
        self.session.ses_generator_token_support = self.tokenizer.model_max_length
        print(f"***The maximum token length for this generator model is: [{self.session.ses_generator_token_support}] tokens")

    
    '''
        Public required implementation.  This is the primary method children classes must implement.
        Basically take the input data chunks as the context, combine with the query, and run through the llm.
        @param self needed for Python syntax
        @param query the question provided by the user, we can/should use our create_prompt method to augment the query later
        @param context the list of chunks that the retriever found that it thought was the most relevent
        @return a string representing the response
    '''
    @abstractmethod
    def public_generate_response(self, query: str, context: list) -> str:
        pass

    '''
        Optionally augment the raw query that the user provided.  The implementation may vary depending on
        the specific instance of the llm being used, but this is a good start.  This implementation also tries
        to check the size of the final prompt against the tokenizer's max value that it can support.  This is just
        an estimate comparison, however.
        @param self Python syntax needed to preten that python is OO
        @param contextChunks array of chunks
        @param query the raw query the user is asking
        @return the prompt, mushing the chunks and the query, approximate number of tokens of the prompt
    '''
    def create_prompt(self, contextChunks, query):
        prompt = f"Context:{contextChunks}\n\nBased on the above context, answer the following question:\n\nQuestion: {query}\n\nAnswer:"
        approx_num_tokens_of_prompt = int(len(prompt) / 3)
        utils.printf(f"Apprx num prompt tokens:       [{approx_num_tokens_of_prompt}]")
        utils.printf(f"Max num tokens for this model: [{self.session.ses_generator_token_support}]")
        if(approx_num_tokens_of_prompt > self.session.ses_generator_token_support):
            utils.printf("* * * * * *    W A R N I N G  * * * * * * *")
            utils.printf(f"YOUR PROMPT MAY BE TOO LONG!")
            utils.printf(f"YOU MAY NEED TO USE SMALLER NUMBER AND SIZE OF CHUNKS OR USE A DIFFERENT GENERATOR/W MORE TOKEN SUPPORT!!!")
            utils.printf(f"Your prompt vs max tokensize: [{approx_num_tokens_of_prompt}]/[{self.session.ses_generator_token_support}]")
            #return f"ERROR: Your prompt vs max tokensize: [{approx_num_tokens_of_prompt}]/[{self.token_max_length}]"

        return prompt,approx_num_tokens_of_prompt