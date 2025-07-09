import requests
import json
from typing import List, Dict, Any
from config import Config

class LLMService:
    """Service for interacting with OpenRouter LLM API"""
    
    def __init__(self):
        """Initialize the LLM service"""
        self.api_key = Config.OPENROUTER_API_KEY
        self.base_url = Config.OPENROUTER_BASE_URL
        self.model = Config.LLM_MODEL
        self.temperature = Config.TEMPERATURE
        self.max_tokens = Config.MAX_TOKENS
    
    def generate_response(self, question: str, context_chunks: List[Dict[str, Any]]) -> str:
        """Generate a response using the LLM with context"""
        # Prepare context from chunks
        context_text = self._prepare_context(context_chunks)
        
        # Create the prompt
        prompt = self._create_prompt(question, context_text)
        
        # Call OpenRouter API
        response = self._call_openrouter(prompt)
        
        return response
    
    def _prepare_context(self, chunks: List[Dict[str, Any]]) -> str:
        """Prepare context from retrieved chunks"""
        context_parts = []
        
        for i, chunk in enumerate(chunks, 1):
            metadata = chunk.get("metadata", {})
            if isinstance(metadata, str):
                try:
                    metadata = json.loads(metadata)
                except:
                    metadata = {}
            
            filename = metadata.get("filename", "Unknown")
            title = metadata.get("title", filename)
            content = chunk.get("content", "")
            
            context_parts.append(f"[{i}] Source: {title} ({filename})\n{content}\n")
        
        return "\n".join(context_parts)
    
    def _create_prompt(self, question: str, context: str) -> str:
        """Create the prompt for the LLM"""
        return f"""You are Chatty, an AI assistant specializing in Australian workers' compensation law and regulations. You provide accurate, helpful information based on the provided context.

Context Information:
{context}

Question: {question}

Instructions:
1. Answer the question based on the provided context
2. If the context doesn't contain enough information to answer the question, say so clearly
3. Provide specific, actionable information when possible
4. Cite your sources using the numbered references [1], [2], etc.
5. Keep your response concise but comprehensive
6. Focus on Australian workers' compensation law and regulations

Answer:"""
    
    def _call_openrouter(self, prompt: str) -> str:
        """Make API call to OpenRouter"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://chatty-chatbot.streamlit.app",
            "X-Title": "Chatty Workers' Compensation Chatbot"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
            else:
                raise Exception(f"OpenRouter API error: {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error calling OpenRouter API: {str(e)}")
        except KeyError as e:
            raise Exception(f"Unexpected response format from OpenRouter: {str(e)}") 