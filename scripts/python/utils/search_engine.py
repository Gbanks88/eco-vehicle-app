#!/usr/bin/env python3

import numpy as np
from typing import List, Dict, Any
from dataclasses import dataclass
from sentence_transformers import SentenceTransformer
import faiss
import json
import logging

@dataclass
class SearchQuery:
    raw_query: str
    processed_query: str
    search_intent: str
    filters: Dict[str, Any]
    user_context: Dict[str, Any]

@dataclass
class Document:
    id: str
    content: str
    metadata: Dict[str, Any]
    embeddings: np.ndarray
    categories: List[str]
    tags: List[str]

class SearchEngine:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.documents = {}
        self.cache = {}
        
    def preprocess_text(self, text: str) -> str:
        """Preprocess text for embedding generation"""
        # Basic preprocessing
        text = text.lower().strip()
        return text
        
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for a list of texts"""
        return self.model.encode(texts, convert_to_tensor=True).numpy()
        
    def add_documents(self, documents: List[Document]):
        """Add documents to the search index"""
        if not documents:
            return
            
        embeddings = []
        for doc in documents:
            self.documents[doc.id] = doc
            embeddings.append(doc.embeddings)
            
        embeddings_array = np.array(embeddings)
        
        if self.index is None:
            dimension = embeddings_array.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            
        self.index.add(embeddings_array)
        
    def search(self, query: SearchQuery, top_k: int = 10) -> List[Document]:
        """Search for documents matching the query"""
        # Check cache
        cache_key = f"{query.raw_query}_{top_k}"
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        # Process query
        processed_text = self.preprocess_text(query.processed_query)
        query_embedding = self.generate_embeddings([processed_text])[0]
        
        # Search
        distances, indices = self.index.search(
            query_embedding.reshape(1, -1),
            top_k
        )
        
        # Get results
        results = []
        for idx in indices[0]:
            doc_id = list(self.documents.keys())[idx]
            doc = self.documents[doc_id]
            
            # Apply filters
            if self._apply_filters(doc, query.filters):
                results.append(doc)
                
        # Update cache
        self.cache[cache_key] = results
        
        return results
        
    def _apply_filters(self, doc: Document, filters: Dict[str, Any]) -> bool:
        """Apply filters to document"""
        if not filters:
            return True
            
        for key, value in filters.items():
            if key in doc.metadata and doc.metadata[key] != value:
                return False
        return True
        
    def optimize_index(self):
        """Optimize the search index"""
        if self.index and isinstance(self.index, faiss.IndexFlat):
            # Convert to IVF index for faster search
            nlist = max(int(len(self.documents) / 10), 1)
            quantizer = faiss.IndexFlatL2(self.index.d)
            new_index = faiss.IndexIVFFlat(quantizer, self.index.d, nlist)
            
            # Train and add vectors
            embeddings = np.array([doc.embeddings for doc in self.documents.values()])
            new_index.train(embeddings)
            new_index.add(embeddings)
            
            self.index = new_index

def main():
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Initialize search engine
    search_engine = SearchEngine()
    
    # Example documents
    docs = [
        Document(
            id="1",
            content="Example document content",
            metadata={"type": "article"},
            embeddings=np.random.rand(384),  # Example dimension
            categories=["tech"],
            tags=["example"]
        )
    ]
    
    # Add documents
    search_engine.add_documents(docs)
    
    # Example search
    query = SearchQuery(
        raw_query="example search",
        processed_query="example search",
        search_intent="informational",
        filters={"type": "article"},
        user_context={"user_id": "123"}
    )
    
    results = search_engine.search(query)
    logging.info(f"Found {len(results)} results")

if __name__ == "__main__":
    main()
