from absretriever import AbsRetriever

class SimpleRetriever(AbsRetriever):
    def public_retrieve_documents(self, query: str) -> list:
        # Convert the query to lowercase
        lowercased_query = query.lower()
        
        return [lowercased_query]

# Example usage
retriever = SimpleRetriever()
query = "What Is A RAG System?"
retrieved_documents = retriever.public_retrieve_documents(query)

print(retrieved_documents)  # Output: ['what is a rag system?']
