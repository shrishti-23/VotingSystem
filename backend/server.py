"""
KrishKalp Live Voting System Server
Connects Frontend <-> Backend <-> Supabase Database
"""

import http.server
import socketserver
import json
import urllib.parse
import os
import sys

# Add parent directory to path so imports work cleanly
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.database import VotingDatabase
from backend.config import IS_SUPABASE_CONFIGURED

PORT = 8000
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")

class DemoRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Enable CORS Headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path

        # API Status Endpoint
        if path == "/api/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response_data = {
                "status": "online",
                "app": "KrishKalp Tech Voting System",
                "is_supabase_connected": IS_SUPABASE_CONFIGURED,
                "database_mode": "Supabase PostgreSQL Database" if IS_SUPABASE_CONFIGURED else "Local Live Demo Store"
            }
            self.wfile.write(json.dumps(response_data).encode("utf-8"))
            return

        # GET /api/candidates
        if path == "/api/candidates":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            candidates_list = VotingDatabase.get_all_candidates()
            self.wfile.write(json.dumps(candidates_list).encode("utf-8"))
            return

        # Serve Frontend Static Files
        if path == "/" or path == "/index.html":
            file_path = os.path.join(FRONTEND_DIR, "index.html")
            self.serve_file(file_path, "text/html")
            return
        else:
            clean_rel = path.lstrip("/").replace("static/", "")
            file_path = os.path.join(FRONTEND_DIR, clean_rel)
            if os.path.exists(file_path):
                content_type = "text/css" if file_path.endswith(".css") else "application/javascript" if file_path.endswith(".js") else "text/plain"
                self.serve_file(file_path, content_type)
                return

        super().do_GET()

    def do_POST(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path

        # POST /api/vote/{candidate_id}
        if path.startswith("/api/vote/"):
            candidate_id = path.split("/")[-1]
            updated_candidate = VotingDatabase.cast_vote(candidate_id)

            if updated_candidate:
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                response = {
                    "message": "Vote recorded successfully!",
                    "candidate": updated_candidate
                }
                self.wfile.write(json.dumps(response).encode("utf-8"))
            else:
                self.send_response(404)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"detail": "Candidate not found"}).encode("utf-8"))
            return

    def serve_file(self, file_path, content_type):
        if os.path.exists(file_path):
            self.send_response(200)
            self.send_header("Content-Type", "application/json" if file_path.endswith(".json") else content_type)
            self.end_headers()
            with open(file_path, "rb") as f:
                self.wfile.write(f.read())
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    active_port = PORT
    httpd = None
    
    for try_port in range(PORT, PORT + 10):
        try:
            httpd = socketserver.TCPServer(("127.0.0.1", try_port), DemoRequestHandler)
            active_port = try_port
            break
        except OSError:
            continue

    if httpd:
        print(f"[SERVER] KrishKalp Live Voting Server starting at http://127.0.0.1:{active_port}")
        httpd.serve_forever()
    else:
        print("[SERVER] Could not bind server to any port in range 8000-8010.")
