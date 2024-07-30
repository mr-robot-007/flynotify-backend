import os
from dotenv import load_dotenv
from fastapi import HTTPException
from supabase import create_client, Client

load_dotenv()

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(url, key)

# Export the Supabase client instance
def get_supabase_client() -> Client:
    return supabase