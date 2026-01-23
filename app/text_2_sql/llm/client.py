from google import genai
from app.text_2_sql.config import Config
import asyncio
from typing import Optional, Dict, Any


class GeminiClient:
    
    _instance = None
    _client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GeminiClient, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        if not Config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        self._client = genai.Client(api_key=Config.GEMINI_API_KEY)
    
    @property
    def client(self):
        return self._client
    
    async def generate_content(self, prompt: str, response_schema: Optional[Dict[str, Any]] = None, **kwargs) -> str:
        config = {}
        
        if response_schema:
            config["response_mime_type"] = "application/json"
            config["response_schema"] = response_schema
        
        response = await self._client.aio.models.generate_content(
            model='models/gemini-2.5-flash',
            contents=prompt,
            config=config if config else None
        )
        
        return response.text


gemini_client = GeminiClient()
