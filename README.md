# RAG Protfolio Project

This project serves to showcase the design of a potential RAG system, that uses the context of a book by Iris Murdoch to supplement the language model's repsonse. 

The tech stack of the solution:

- **Neo4j** as a vector DB, wiht potenital for future expansion into knowledge graph to improve context
- **Ollama** for embeddings + LLM responses (`llama3.1:8b-instruct-q5_1`)
- **Python** scripting engine
- **.epub** book as source

## Pipeline

1. `scraper.py`: Parse `.epub` → insert paragraphs into Neo4j `TEXT` nodes with `text` attribute.
2. `vectorise.py`: Embed `TEXT.text` via Ollama → save to `TEXT.embedding`.
3. `search.py "query..."`: 
   Embed query
   - Cosine similarity search
   - Top 3 results → prompt LLM for response.

## Usage

```bash
# 1. Extract and insert
python scraper.py

# 2. Vectorize text of TEXT node into Text.embedding
python vectorise.py TEXT text embedding

# 3. Ask something
python search.py "What is attention?"
```

## Next Steps
- Smarter chunking
- Relevance feedback loop
- Add UI
- Streamed responses
- Metadata like chapters, location