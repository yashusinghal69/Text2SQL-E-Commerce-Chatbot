import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    SUPABASE_DB_PASSWORD = os.getenv("SUPABASE_DB_PASSWORD")
    @classmethod
    def validate(cls):
        missing = [k for k, v in cls.__dict__.items() if not k.startswith("__") and not callable(v) and not v]
        if missing:
            print(f"Warning: Missing environment variables: {', '.join(missing)}")
