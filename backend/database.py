import os
import sys
import json
import urllib.request
import urllib.error
import ssl
from typing import List, Dict, Any, Optional

from backend.config import SUPABASE_URL, SUPABASE_KEY, IS_SUPABASE_CONFIGURED

# Create SSL context that bypasses Windows local CA certificate issues
ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

# Clean Base URL & Headers
CLEAN_SUPABASE_URL = SUPABASE_URL.rstrip('/')
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# Initial Candidates Template if table is empty
SEED_CANDIDATES = [
    {"id": "1", "name": "Python FastAPI", "category": "Backend Framework", "votes": 12, "icon": "⚡"},
    {"id": "2", "name": "React & JavaScript", "category": "Frontend UI Framework", "votes": 18, "icon": "💻"},
    {"id": "3", "name": "Supabase PostgreSQL", "category": "Cloud Database System", "votes": 15, "icon": "🐘"},
    {"id": "4", "name": "AI Pair Programmer", "category": "Developer Tools", "votes": 25, "icon": "🤖"}
]

class VotingDatabase:
    @staticmethod
    def get_all_candidates() -> List[Dict[str, Any]]:
        if not IS_SUPABASE_CONFIGURED:
            print("[INFO] Supabase credentials not configured in .env")
            return SEED_CANDIDATES

        try:
            url = f"{CLEAN_SUPABASE_URL}/rest/v1/candidates?select=*&order=id"
            req = urllib.request.Request(url, headers=HEADERS, method="GET")
            
            with urllib.request.urlopen(req, context=ssl_ctx, timeout=6) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                
                if data and len(data) > 0:
                    print(f"[SUCCESS] Fetched {len(data)} candidates from Supabase PostgreSQL!")
                    return data
                else:
                    # Auto-seed candidates if table is empty
                    print("[INFO] Candidates table is empty. Auto-seeding initial candidates into Supabase...")
                    VotingDatabase._seed_candidates()
                    return SEED_CANDIDATES
        except Exception as err:
            print(f"[ERROR] Supabase fetch error: {err}")
            return SEED_CANDIDATES

    @staticmethod
    def cast_vote(candidate_id: str) -> Optional[Dict[str, Any]]:
        if not IS_SUPABASE_CONFIGURED:
            print("[ERROR] Supabase is not configured.")
            return None

        try:
            # 1. Fetch current votes for candidate
            url_get = f"{CLEAN_SUPABASE_URL}/rest/v1/candidates?id=eq.{candidate_id}&select=*"
            req_get = urllib.request.Request(url_get, headers=HEADERS, method="GET")
            
            with urllib.request.urlopen(req_get, context=ssl_ctx, timeout=6) as resp_get:
                rows = json.loads(resp_get.read().decode("utf-8"))
                
                if rows:
                    candidate = rows[0]
                    current_votes = candidate.get("votes", 0)
                    new_votes = current_votes + 1

                    # 2. Update vote count in Supabase PostgreSQL via REST PATCH
                    url_patch = f"{CLEAN_SUPABASE_URL}/rest/v1/candidates?id=eq.{candidate_id}"
                    payload = json.dumps({"votes": new_votes}).encode("utf-8")
                    req_patch = urllib.request.Request(url_patch, data=payload, headers=HEADERS, method="PATCH")
                    
                    with urllib.request.urlopen(req_patch, context=ssl_ctx, timeout=6) as resp_patch:
                        print(f"[SUCCESS] Supabase PostgreSQL Updated Candidate {candidate_id}: {current_votes} -> {new_votes}")
                        candidate["votes"] = new_votes
                        return candidate
                else:
                    print(f"[WARNING] Candidate {candidate_id} not found in Supabase.")
        except Exception as err:
            print(f"[ERROR] Supabase vote update error: {err}")

        return None

    @staticmethod
    def _seed_candidates():
        try:
            url_post = f"{CLEAN_SUPABASE_URL}/rest/v1/candidates"
            payload = json.dumps(SEED_CANDIDATES).encode("utf-8")
            req_post = urllib.request.Request(url_post, data=payload, headers=HEADERS, method="POST")
            with urllib.request.urlopen(req_post, context=ssl_ctx, timeout=6) as resp:
                print("[SUCCESS] Auto-seeded candidates into Supabase Cloud Database!")
        except Exception as err:
            print(f"[WARNING] Seed error: {err}")
