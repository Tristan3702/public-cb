import openai
from typing import List, Dict, Any
from config import Config

class EmbeddingService:
    """Service for handling OpenAI embeddings"""
    
    def __init__(self):
        """Initialize the embedding service"""
        openai.api_key = Config.OPENAI_API_KEY
        self.model = Config.EMBEDDING_MODEL
    
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding for a single text"""
        try:
            response = openai.embeddings.create(
                model=self.model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            raise Exception(f"Error getting embedding: {str(e)}")
    
    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for multiple texts in batch"""
        try:
            response = openai.embeddings.create(
                model=self.model,
                input=texts
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            raise Exception(f"Error getting batch embeddings: {str(e)}")
    
    def embed_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add embeddings to a list of chunks"""
        texts = [chunk["content"] for chunk in chunks]
        embeddings = self.get_embeddings_batch(texts)
        
        for i, embedding in enumerate(embeddings):
            chunks[i]["embedding"] = embedding
        
        return chunks 