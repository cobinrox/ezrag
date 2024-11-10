import os
import sys
from abc import ABC, abstractmethod

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
from utils import utils


'''
    Abstract class for a retriever.  A retriever relies on a chunker class to help with chopping up
    the data corpus; an embedder engine to encode the chunks; and a vector search engine to compare
    an input question to the chunks, as embeddings.
'''
class AbsRetriever(ABC):
    '''
        Types of similarity algorithms that can be used to compare a query to doc chunks
    '''
    EUCLIDIAN_DISTANCE   = "EUCLIDIAN"   # numbers closer to 0.0 mean good results/simlarity
    DOT_PRODUCT_DISTANCE = "DOT_PRODUCT"
    COSINE_DISTANCE      = "COSINE"      # numbers closer to 1.0 mean good results/similarity

    '''
        header for a CSV file that contains stats info about the chunks that we create
    '''
    CHUNK_STATS_CSV_HEADER  = "SessionNum,VectorEngine,SimilarityType,SimilarityScore,ReretreiveSimType,ReretreivedScore,ApproxPercentScore,ChunkSize,ChunkFileName,OffsetInFile"
 
    
    '''
        Constructor.
        @param self Python idiom required for syntax.
        @param session contains configuration information such as the location of the docs to query,
                       and stats/results information
    '''
    def __init__(self, session):
        self.session = session
        self.chunker   = None  # place holder for optional chunker association
        self.generator = None  # place holder optional generator association

    '''
        Use these to set a chunker and/or generator, if needed
    '''
    def injectChunker(self,chunker):
        self.chunker  = chunker        
    def injectGenerator(self,generator):
        self.generator  = generator

    '''
        Utility method to take a similarity score between a query and a chunk and, based on the
        type of the similary score that was original used, give an approximation of a percentage
        of how strong the score is.  For example, if the scoring type were EUCLIDIAN and the score
        value were 0.1, it'd be a pretty high percentage.
        @param self Python idiom needed for syntax
        @param value the similarity score value, as a string (sorry)
        @param metric_type similarity score type (see the DISTANCE type definitions at the top of this file)
        @return string representing apprx percent value
    '''
    def approx_percent_score(self,  value: str, metric_type: str, max_threshold) -> str:
        # Convert the second input to a float
        try:
            float_value = float(value)
        except ValueError:
            raise ValueError("The second input must be a string representing a numeric value.")

        # Define the maximum threshold for EUCLIDIAN and DOT_PRODUCT to normalize the score
        #max_threshold = 2.0  # Adjust as needed based on your context

        # Calculate the percentage of closeness
        if metric_type == "EUCLIDIAN" or metric_type == "DOT_PRODUCT":
            if float_value < 0:
                return "0.00%"  # Negative values are not valid in this context, closest to 0%
            score = max(0.0, 100 * (1 - float_value / max_threshold))
        
        elif metric_type == "COSINE":
            if not (0 <= float_value <= 1):
                return "0.00%"  # Invalid value for cosine similarity, closest to 0%
            score = 100 * float_value
        
        else:
            raise ValueError("The first input must be 'EUCLIDIAN', 'DOT_PRODUCT', or 'COSINE'.")

        # Return the score as a formatted string rounded to 2 decimal places
        return f"{round(score, 2):.2f}%"
               
    '''
        Internal, but required implementation to take the document list and embed them
        @param self Python idiom required for syntax
    '''
    @abstractmethod
    def _create_doc_embeddings(self):
        pass
    
    '''
        Public, required implementation to take a query, run the retrieval augmentation algorithm,
        and return a list of the top "k" chunks that match the query string the best
        @param self Python idiom required for syntax
        @param query the question the user wants to ask against the docs
        @return list a list of chunks at the least, but can also be a list of other information icluding the chunks
    '''
    @abstractmethod
    def public_retrieve_documents(self, query: str) -> list:
        pass
 