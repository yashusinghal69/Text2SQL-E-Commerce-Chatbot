from openai import AsyncOpenAI
from app.text_2_sql.config import Config
import asyncio
import json
from typing import Optional, Dict, Any


class OpenAIClient:
    
    _instance = None
    _client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OpenAIClient, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        if not Config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self._client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)
    
    @property
    def client(self):
        return self._client
    
    async def generate_content(self, prompt: str, response_schema: Optional[Dict[str, Any]] = None, **kwargs) -> str:
        """
        Generate content using OpenAI API.
        
        Args:
            prompt: The prompt text
            response_schema: Optional JSON schema for structured output
            **kwargs: Additional parameters
            
        Returns:
            str: The generated text response
        """
        # If using JSON mode, ensure prompt mentions "json" (OpenAI requirement)
        if response_schema:
            if "json" not in prompt.lower():
                prompt = prompt + "\n\nRespond with valid JSON format."
        
        messages = [{"role": "user", "content": prompt}]
        
        # Prepare kwargs for API call
        api_kwargs = {
            "model": "gpt-4o-mini",
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
        }
        
        # Add JSON mode if schema is provided
        if response_schema:
            api_kwargs["response_format"] = {"type": "json_object"}
        
        response = await self._client.chat.completions.create(**api_kwargs)
        
        return response.choices[0].message.content


# Singleton instance
openai_client = OpenAIClient()
# Backward compatibility alias
gemini_client = openai_client
