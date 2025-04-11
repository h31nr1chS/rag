from langchain_community.vectorstores import Neo4jVector
import os
from dotenv import load_dotenv
import sys
import requests

load_dotenv()

# Check command-line arguments
if len(sys.argv) < 4:
    print("Usage: python script.py <NODE_LABEL> <VECTOR_PROPERTY> <EMBEDDING_PROPERTY>")
    sys.exit(1)

NODE = sys.argv[1]
VECTOR_PROPS = [sys.argv[2]]
EMBEDDING = sys.argv[3]

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

# Initialize our Ollama embeddings
ollama_embeddings = OllamaEmbeddings()
print(f"Using Ollama API for embeddings with model: {ollama_embeddings.model_name}")

# Set up the vector store connection
graph = Neo4jVector.from_existing_graph(
    embedding=ollama_embeddings,
    url=os.environ.get("NEO4J_HOST"),
    username=os.environ.get("NEO4J_USER"),
    password=os.environ.get("NEO4J_PASSWORD"),
    node_label=NODE,
    index_name=f'{NODE}_index',
    text_node_properties=VECTOR_PROPS,
    embedding_node_property=EMBEDDING,
    database=os.environ.get("NEO4J_DB")
)

print(f"Successfully connected to Neo4j vector store")
print(f"Node label: {NODE}")
print(f"Vector properties: {VECTOR_PROPS}")
print(f"Embedding property: {EMBEDDING}")
print(f"Index name: {NODE}_index")