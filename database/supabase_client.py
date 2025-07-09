import json
from typing import List, Dict, Any, Optional
from supabase import create_client, Client
from config import Config

class SupabaseClient:
    """Client for interacting with Supabase database"""
    
    def __init__(self):
        """Initialize Supabase client"""
        self.client: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
    
    def insert_document(self, filename: str, title: str, content_type: str, file_size: int) -> str:
        """Insert a new document and return its ID"""
        data = {
            "filename": filename,
            "title": title,
            "content_type": content_type,
            "file_size": file_size
        }
        
        result = self.client.table("chat_bot_documents").insert(data).execute()
        return result.data[0]["id"]
    
    def insert_chunks(self, document_id: str, chunks: List[Dict[str, Any]]) -> None:
        """Insert document chunks with embeddings"""
        chunk_data = []
        
        for i, chunk in enumerate(chunks):
            chunk_data.append({
                "document_id": document_id,
                "chunk_index": i,
                "content": chunk["content"],
                "metadata": json.dumps(chunk["metadata"]),
                "embedding": chunk["embedding"]
            })
        
        self.client.table("chat_bot_document_chunks").insert(chunk_data).execute()
    
    def search_similar_chunks(self, query_embedding: List[float], top_k: int = None) -> List[Dict[str, Any]]:
        """Search for similar chunks using vector similarity"""
        if top_k is None:
            top_k = Config.TOP_K_RESULTS
        
        # Call the match_documents function
        result = self.client.rpc(
            "chat_bot_match_documents",
            {
                "query_embedding": query_embedding,
                "match_threshold": 0.78,
                "match_count": top_k
            }
        ).execute()
        
        return result.data
    
    def get_document_info(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get document information by ID"""
        result = self.client.table("chat_bot_documents").select("*").eq("id", document_id).execute()
        
        if result.data:
            return result.data[0]
        return None
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        """Get all documents"""
        result = self.client.table("chat_bot_documents").select("*").order("created_at", desc=True).execute()
        return result.data
    
    def delete_document(self, document_id: str) -> None:
        """Delete a document and all its chunks (cascade)"""
        self.client.table("chat_bot_documents").delete().eq("id", document_id).execute()
    
    def get_chunk_count(self, document_id: str) -> int:
        """Get the number of chunks for a document"""
        result = self.client.table("chat_bot_document_chunks").select("id", count="exact").eq("document_id", document_id).execute()
        return result.count or 0 