import os
import re
from typing import List, Dict, Any
from PyPDF2 import PdfReader
import markdown
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.text_splitter import MarkdownHeaderTextSplitter
from langchain.text_splitter import HTMLHeaderTextSplitter
from langchain.text_splitter import TokenTextSplitter
from config import Config

class DocumentProcessor:
    """Process and chunk documents for vector storage"""
    
    def __init__(self):
        """Initialize the document processor"""
        # Semantic-aware text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
            length_function=len,
            separators=[
                "\n\n",  # Paragraphs
                "\n",    # Lines
                ". ",    # Sentences
                "! ",    # Exclamations
                "? ",    # Questions
                "; ",    # Semi-colons
                ": ",    # Colons
                ", ",    # Commas
                " ",     # Words
                ""       # Characters
            ]
        )
        
        # Markdown header splitter for semantic structure
        self.markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[
                ("#", "Header 1"),
                ("##", "Header 2"),
                ("###", "Header 3"),
                ("####", "Header 4"),
                ("#####", "Header 5"),
                ("######", "Header 6"),
            ]
        )
        
        # Token-based splitter for more precise control
        self.token_splitter = TokenTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
            encoding_name="cl100k_base"  # OpenAI tokenizer
        )
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from a PDF file"""
        try:
            reader = PdfReader(file_path)
            text = ""
            
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting text from PDF {file_path}: {str(e)}")
    
    def extract_text_from_markdown(self, file_path: str) -> str:
        """Extract text from a Markdown file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Convert markdown to plain text
            html = markdown.markdown(content)
            # Remove HTML tags
            text = re.sub(r'<[^>]+>', '', html)
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting text from Markdown {file_path}: {str(e)}")
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from a file based on its extension"""
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif file_extension in ['.md', '.markdown']:
            return self.extract_text_from_markdown(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
    
    def chunk_text(self, text: str, filename: str, title: str | None = None) -> List[Dict[str, Any]]:
        """Split text into chunks with semantic awareness"""
        if not title:
            title = os.path.splitext(os.path.basename(filename))[0]
        
        file_extension = os.path.splitext(filename)[1].lower()
        
        # Choose the best splitter based on file type and content
        if file_extension in ['.md', '.markdown']:
            chunks = self._chunk_markdown_semantic(text, filename, title)
        else:
            chunks = self._chunk_general_semantic(text, filename, title)
        
        return chunks
    
    def _chunk_markdown_semantic(self, text: str, filename: str, title: str) -> List[Dict[str, Any]]:
        """Semantic chunking for Markdown documents"""
        try:
            # First, split by headers to preserve document structure
            header_splits = self.markdown_splitter.split_text(text)
            
            chunks = []
            chunk_index = 0
            
            for split in header_splits:
                # Get header information
                header_info = split.metadata.get('Header 1', '') or split.metadata.get('Header 2', '') or split.metadata.get('Header 3', '')
                
                # Further split by content if needed
                if len(split.page_content) > Config.CHUNK_SIZE:
                    # Use token splitter for large sections
                    sub_chunks = self.token_splitter.split_text(split.page_content)
                else:
                    sub_chunks = [split.page_content]
                
                # Create chunks with semantic metadata
                for i, chunk_text in enumerate(sub_chunks):
                    chunk = {
                        "content": chunk_text.strip(),
                        "metadata": {
                            "filename": filename,
                            "title": title,
                            "chunk_index": chunk_index,
                            "section_header": header_info,
                            "file_type": "markdown",
                            "semantic_split": True,
                            "sub_chunk_index": i,
                            "total_sub_chunks": len(sub_chunks)
                        }
                    }
                    chunks.append(chunk)
                    chunk_index += 1
            
            # Update total chunks count
            for chunk in chunks:
                chunk["metadata"]["total_chunks"] = len(chunks)
            
            return chunks
            
        except Exception as e:
            # Fallback to general semantic chunking
            print(f"Markdown semantic chunking failed, falling back to general: {e}")
            return self._chunk_general_semantic(text, filename, title)
    
    def _chunk_general_semantic(self, text: str, filename: str, title: str) -> List[Dict[str, Any]]:
        """Semantic chunking for general documents"""
        # Use token-based splitting for more precise control
        text_chunks = self.token_splitter.split_text(text)
        
        # Create chunk objects with enhanced metadata
        chunks = []
        for i, chunk_text in enumerate(text_chunks):
            # Extract semantic information
            semantic_info = self._extract_semantic_info(chunk_text)
            
            chunk = {
                "content": chunk_text.strip(),
                "metadata": {
                    "filename": filename,
                    "title": title,
                    "chunk_index": i,
                    "total_chunks": len(text_chunks),
                    "file_type": os.path.splitext(filename)[1].lower(),
                    "semantic_split": True,
                    "content_type": semantic_info["content_type"],
                    "key_topics": semantic_info["key_topics"],
                    "word_count": len(chunk_text.split())
                }
            }
            chunks.append(chunk)
        
        return chunks
    
    def _extract_semantic_info(self, text: str) -> Dict[str, Any]:
        """Extract semantic information from text chunk"""
        # Simple semantic analysis
        text_lower = text.lower()
        
        # Determine content type
        content_type = "general"
        if any(word in text_lower for word in ["claim", "injury", "compensation", "benefits"]):
            content_type = "claims"
        elif any(word in text_lower for word in ["law", "regulation", "policy", "rule"]):
            content_type = "legal"
        elif any(word in text_lower for word in ["process", "step", "procedure", "how to"]):
            content_type = "procedural"
        elif any(word in text_lower for word in ["contact", "phone", "email", "address"]):
            content_type = "contact"
        
        # Extract key topics (simple keyword extraction)
        key_topics = []
        keywords = [
            "workers compensation", "injury", "claim", "benefits", "medical", 
            "rehabilitation", "return to work", "permanent impairment", "weekly payments",
            "employer", "employee", "insurance", "legal", "appeal", "dispute"
        ]
        
        for keyword in keywords:
            if keyword in text_lower:
                key_topics.append(keyword)
        
        return {
            "content_type": content_type,
            "key_topics": key_topics
        }
    
    def process_document(self, file_path: str, title: str | None = None) -> Dict[str, Any]:
        """Process a document and return chunks with metadata"""
        # Extract text
        text = self.extract_text(file_path)
        
        # Get file info
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        content_type = os.path.splitext(filename)[1].lower()
        
        if not title:
            title = os.path.splitext(filename)[0]
        
        # Chunk the text
        chunks = self.chunk_text(text, filename, title)
        
        return {
            "filename": filename,
            "title": title,
            "content_type": content_type,
            "file_size": file_size,
            "chunks": chunks,
            "total_chunks": len(chunks)
        } 