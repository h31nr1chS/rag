from langchain_community.vectorstores import Neo4jVector
import os
from dotenv import load_dotenv
from pprint import pprint
import sys
import requests
import numpy as np

load_dotenv()

# Check if enough command line arguments are provided
if len(sys.argv) < 2:
    print("Usage: python search.py <SEARCH_QUERY> [NODE_LABEL] [VECTOR_PROPERTIES] [EMBEDDING_PROPERTY]")
    sys.exit(1)

# Command line arguments
SEARCH_QUERY = sys.argv[1]
NODE = sys.argv[2] if len(sys.argv) > 2 else "Document"
VECTOR_PROPS = [sys.argv[3]] if len(sys.argv) > 3 else ["text"]
EMBEDDING = sys.argv[4] if len(sys.argv) > 4 else "embedding"

# Define Ollama embedding function
class OllamaEmbeddings:
    def __init__(self, model_name="llama3.1:8b-instruct-q5_1", base_url="http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        self.embed_url = f"{base_url}/api/embeddings"
    
    def embed_documents(self, texts):
        """Embed a list of documents using Ollama API"""
        all_embeddings = []
        for text in texts:
            embeddings = self._get_embeddings(text)
            all_embeddings.append(embeddings)
        return all_embeddings
    
    def embed_query(self, text):
        """Embed a query using Ollama API"""
        return self._get_embeddings(text)
    
    def _get_embeddings(self, text):
        """Get embeddings for a single text using Ollama API"""
        payload = {
            "model": self.model_name,
            "prompt": text
        }
        
        response = requests.post(self.embed_url, json=payload)
        
        if response.status_code == 200:
            embedding = response.json().get("embedding", [])
            return embedding
        else:
            raise Exception(f"Error from Ollama API: {response.text}")

# Initialize the Ollama embeddings
ollama_embeddings = OllamaEmbeddings()

# Set up the vector store connection
graph = Neo4jVector.from_existing_graph(
    embedding=ollama_embeddings,
    url=os.environ.get("NEO4J_HOST"),
    username=os.environ.get("NEO4J_USER"),
    password=os.environ.get("NEO4J_PASSWORD"),
    index_name=f'{NODE}_index',
    node_label=NODE,
    text_node_properties=VECTOR_PROPS,
    embedding_node_property=EMBEDDING,
    database=os.environ.get("NEO4J_DB")
)

# Perform the similarity search
print(f"Searching for: '{SEARCH_QUERY}'")
results = graph.similarity_search_with_score(SEARCH_QUERY, k=3)

prompt = f"""
Based on the following information, please provide a concise and helpful response to the query: "{SEARCH_QUERY}".
The reader is an intelligent non-expert. Answer in authority, do not say "Based on the provided text" or any such qualifiers.
{results}
Response:
"""

# Send request to Ollama API
ollama_url = "http://localhost:11434/api/generate"
ollama_request = {
    "model": "llama3.1:8b-instruct-q5_1",  # Using the same model for consistency
    "prompt": prompt,
    "stream": False
}

print("Querying LLM...")
response = requests.post(ollama_url, json=ollama_request)
answer = response.json()["response"]

print("\nOllama's Answer:")
print(answer)