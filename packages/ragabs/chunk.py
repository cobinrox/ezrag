'''
   Holder for information relating to an individual chunk of text.  Arrays of these are
   usually held and manipulated by the chunker and the retriever.  The iformation can then
   be written out to a csv file for help with tracking stats and doing deeper investigations.
   These chunk objs are associated with an array of chunks that are created by the chunker,
   so there is a 1:1 relationship between each chunk in the chunk array and one of these.
'''
class Chunk:
    def __init__(self):
         self.chk_name        = ""    # a name given to the chunk
         self.chk_idx         = -1    # index into the array of chunks created by chunker
         self.chk_contents    = ""    # not used: actual chunk value, we actually store the
                                      # chunk in a separate array, but may make more sense
                                      # to actually move it to here in the future
         self.chk_summary     =  ""   # the first 3 chars and the last 3 chars of the chunk
                                      # value, this is handy for debugging/monitoring what the
                                      # chunker and retriever are doing
         self.chk_len         =-1     # size of the chunk, i.e. num chars
         self.chk_filename    =""     # filename where the chunk was extracted from
         self.chk_offsetInFile=-1     # offset wihtin the file where the chunk came from
         self.chk_dummy       =""     # not used
         self.chk_size        =-1     # length of the chunk

         # this is filled out at encoding time by retriever
         self.chk_embedding=None      # embedding value of the chunk

         # determined at retrieval time
         self.chk_similarity_score_type = "" # type of initial scoring that will be used when
                                             # comparing this chunk to the user's query, see the
                                             # values in the AbsRetriever for valid values
         self.chk_initial_score=-1           # initial score that the retriever's vector/search
                                             # engine found for this chunk when comparing to the
                                             # user's query
         # determined at re-retrieval time
         self.chk_reretrieved_score_type = "COSINE" # for re-retrieval, the typy of scoring used,
                                                    # right now we only do cosine for re-retrieval
         self.chk_reretrieved_score=-1       # re-retrieval score
         self.chk_approx_percent_score="0"   # for ease-of view, an approximation of the score
                                             # as if it were a percentage, this is not perfectly
                                             # accurate, but it makes it easier to read and grok
                                             # for a user when looking at the chunk score
        