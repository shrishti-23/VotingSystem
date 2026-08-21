import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

IS_SUPABASE_CONFIGURED = bool(
    SUPABASE_URL and 
    SUPABASE_KEY and 
    "your-project" not in SUPABASE_URL and 
    "your-anon-key" not in SUPABASE_KEY
)
