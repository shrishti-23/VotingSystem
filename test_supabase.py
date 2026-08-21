import os
import ssl
import httpx
from dotenv import load_dotenv

# Monkey-patch httpx to disable SSL verification for Windows local issuer errors
_original_httpx_init = httpx.Client.__init__
def _patched_httpx_init(self, *args, **kwargs):
    kwargs['verify'] = False
    _original_httpx_init(self, *args, **kwargs)
httpx.Client.__init__ = _patched_httpx_init

load_dotenv()

from supabase import create_client

url = os.getenv("SUPABASE_URL", "")
key = os.getenv("SUPABASE_KEY", "")

print(f"SUPABASE_URL: {url}")
print(f"SUPABASE_KEY length: {len(key)}")

try:
    client = create_client(url, key)
    print("[SUCCESS] Supabase client initialized successfully!")

    # 1. Test Select
    print("\n--- 1. Testing SELECT on 'candidates' table ---")
    select_res = client.table("candidates").select("*").execute()
    print(f"SELECT data: {select_res.data}")

    if not select_res.data or len(select_res.data) == 0:
        print("[WARNING] 'candidates' table is empty. Inserting test candidate...")
        test_candidates = [
            {"id": "1", "name": "Python FastAPI", "category": "Backend Framework", "votes": 12, "icon": "⚡"},
            {"id": "2", "name": "React & JavaScript", "category": "Frontend UI Framework", "votes": 18, "icon": "💻"},
            {"id": "3", "name": "Supabase PostgreSQL", "category": "Cloud Database System", "votes": 15, "icon": "🐘"},
            {"id": "4", "name": "AI Pair Programmer", "category": "Developer Tools", "votes": 25, "icon": "🤖"}
        ]
        client.table("candidates").insert(test_candidates).execute()
        select_res = client.table("candidates").select("*").execute()
        print(f"SELECT data after insert: {select_res.data}")

    if select_res.data:
        first_row = select_res.data[0]
        first_id = first_row.get("id")
        first_votes = first_row.get("votes", 0)
        print(f"First row: id={first_id}, votes={first_votes}")

        # 2. Test Update
        print(f"\n--- 2. Testing UPDATE for id={first_id} ---")
        new_votes = first_votes + 1
        
        update_res = client.table("candidates").update({"votes": new_votes}).eq("id", first_id).execute()
        print(f"UPDATE response data: {update_res.data}")

        # Re-fetch to verify
        verify_res = client.table("candidates").select("*").eq("id", first_id).execute()
        print(f"VERIFY after update: {verify_res.data}")

except Exception as err:
    print(f"\n[EXCEPTION] {type(err).__name__} -> {err}")
