#!/usr/bin/env python3
"""
Document Uploader for Chatty Workers' Compensation Chatbot
Uploads and processes documents for vector storage in Supabase
"""

import os
import sys
from typing import List
from pathlib import Path

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from database.supabase_client import SupabaseClient
from utils.document_processor import DocumentProcessor
from utils.embedding_service import EmbeddingService

def upload_documents(file_paths: List[str]) -> None:
    """
    Upload and process documents for vector storage
    
    Args:
        file_paths: List of file paths to process and upload
    """
    try:
        # Validate configuration
        Config.validate()
        
        # Initialize services
        supabase_client = SupabaseClient()
        document_processor = DocumentProcessor()
        embedding_service = EmbeddingService()
        
        print("🚀 Starting document upload process...")
        
        for file_path in file_paths:
            if not os.path.exists(file_path):
                print(f"❌ File not found: {file_path}")
                continue
            
            print(f"\n📄 Processing: {file_path}")
            
            try:
                # Process the document
                doc_info = document_processor.process_document(file_path)
                print(f"   ✓ Extracted {doc_info['total_chunks']} chunks")
                
                # Add embeddings to chunks
                print("   🔄 Generating embeddings...")
                chunks_with_embeddings = embedding_service.embed_chunks(doc_info['chunks'])
                print("   ✓ Embeddings generated")
                
                # Insert document into database
                print("   💾 Storing in database...")
                document_id = supabase_client.insert_document(
                    filename=doc_info['filename'],
                    title=doc_info['title'],
                    content_type=doc_info['content_type'],
                    file_size=doc_info['file_size']
                )
                
                # Insert chunks
                supabase_client.insert_chunks(document_id, chunks_with_embeddings)
                print(f"   ✓ Document uploaded successfully (ID: {document_id})")
                
            except Exception as e:
                print(f"   ❌ Error processing {file_path}: {str(e)}")
                continue
        
        print("\n✅ Document upload process completed!")
        
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        sys.exit(1)

def main():
    """Main function for command-line usage"""
    if len(sys.argv) < 2:
        print("Usage: python document_uploader.py <file1> [file2] [file3] ...")
        print("Example: python document_uploader.py docs/workers_comp_guide.pdf docs/regulations.md")
        sys.exit(1)
    
    file_paths = sys.argv[1:]
    upload_documents(file_paths)

if __name__ == "__main__":
    main() 