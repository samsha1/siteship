# /backend/supabase_client.py
# Handles Supabase database and storage operations.

import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    raise EnvironmentError("SUPABASE_URL and SUPABASE_KEY must be set in the environment.")

# Initialize the Supabase client
supabase: Client = create_client(url, key)

print("Supabase client initialized successfully.")