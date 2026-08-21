from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List
import os

from backend.models import CandidateResponse, VoteRequest
from backend.database import VotingDatabase
from backend.config import IS_SUPABASE_CONFIGURED

app = FastAPI(
    title="KrishKalp Tech Voting System API",
    description="Simple & Clean Voting App with FastAPI and Supabase PostgreSQL",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Status Endpoint
@app.get("/api/status")
def get_api_status():
    return {
        "status": "online",
        "app": "KrishKalp Tech Voting System",
        "is_supabase_connected": IS_SUPABASE_CONFIGURED,
        "database_mode": "Supabase PostgreSQL Database" if IS_SUPABASE_CONFIGURED else "Local Live Demo Store"
    }

# GET All Candidates & Vote Counts
@app.get("/api/candidates", response_model=List[CandidateResponse])
def get_candidates():
    return VotingDatabase.get_all_candidates()

# POST Cast a Vote for Candidate
@app.post("/api/vote/{candidate_id}")
def vote_for_candidate(candidate_id: str):
    updated = VotingDatabase.cast_vote(candidate_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return {"message": "Vote recorded successfully!", "candidate": updated}

# Serve Frontend Static Web Files
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
