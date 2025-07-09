#!/usr/bin/env python3
"""
Test script to connect to Supabase and count rows in chat_bot_documents table
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv(override=True)

def test_supabase_connection():
    """Test connection to Supabase and count documents"""
    try:
        # Get Supabase credentials
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            print("❌ Missing Supabase credentials in .env file")
            print("   Please ensure SUPABASE_URL and SUPABASE_KEY are set")
            return
        
        # Create Supabase client
        print("🔌 Connecting to Supabase...")
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Test connection by counting documents
        print("📊 Counting rows in chat_bot_documents table...")
        result = supabase.table("chat_bot_documents").select("id", count="exact").execute()
        
        document_count = result.count or 0
        print(f"✅ Connection successful!")
        print(f"📄 Found {document_count} documents in chat_bot_documents table")
        
        # Also count chunks
        print("📊 Counting rows in chat_bot_document_chunks table...")
        chunks_result = supabase.table("chat_bot_document_chunks").select("id", count="exact").execute()
        
        chunks_count = chunks_result.count or 0
        print(f"📝 Found {chunks_count} chunks in chat_bot_document_chunks table")
        
        # Show table structure
        print("\n📋 Table Structure:")
        print("   - chat_bot_documents: Stores document metadata")
        print("   - chat_bot_document_chunks: Stores document chunks with embeddings")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        print("\n🔧 Troubleshooting tips:")
        print("   1. Check your .env file has correct SUPABASE_URL and SUPABASE_KEY")
        print("   2. Ensure the database schema has been created (run database/schema.sql)")
        print("   3. Verify your Supabase project has pgvector extension enabled")
        return False

if __name__ == "__main__":
    print("🏥 Chatty - Supabase Connection Test")
    print("=" * 40)
    
    success = test_supabase_connection()
    
    if success:
        print("\n🎉 Test completed successfully!")
    else:
        print("\n💥 Test failed. Please check your configuration.") 