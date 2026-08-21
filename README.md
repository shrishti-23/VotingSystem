# 🗳️DEVTech Voting System (Demo Project)

A super simple, high-impact Full-Stack Voting System designed for **KrishKalp Intern Workshops**.

---

## 📋 Step-by-Step Supabase Database Setup Guide

Follow these simple steps to set up your live Supabase PostgreSQL database:

### Step 1: Create a Free Supabase Account & Project
1. Open [https://supabase.com](https://supabase.com) and log in.
2. Click **+ New Project**.
3. Name your project: `krishkalp-voting-db`.
4. Enter a secure database password and choose a region (e.g. Mumbai / Singapore).
5. Click **Create new project** and wait 1 minute for initialization.

---

### Step 2: Create the `candidates` Table
1. In your Supabase Dashboard, click **SQL Editor** on the left menu.
2. Click **+ New query**.
3. Copy and paste the following SQL code:

```sql
-- 1. Create the candidates table
CREATE TABLE candidates (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  category TEXT NOT NULL,
  votes INT DEFAULT 0,
  icon TEXT DEFAULT '⚡'
);

-- 2. Insert initial voting choices
INSERT INTO candidates (id, name, category, votes, icon) VALUES
('1', 'Python FastAPI', 'Backend Framework', 12, '🐍'),
('2', 'React & JavaScript', 'Frontend UI Framework', 18, '⚡'),
('3', 'Supabase PostgreSQL', 'Cloud Database System', 15, '🐘'),
('4', 'AI Pair Programmer', 'Developer Tools', 25, '🤖');

-- 3. Enable Public Read and Write Access Policy
ALTER TABLE candidates ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow public access" ON candidates FOR ALL USING (true);
```

4. Click **Run** (▶) at the bottom right. You will see `Success. No rows returned`.

---

### Step 3: Copy Your API Credentials into `.env`
1. In Supabase Dashboard, click **Project Settings** (gear icon ⚙️ at bottom left) &rarr; **API**.
2. Copy:
   * **Project URL**: `https://xyz...supabase.co`
   * **anon public key**: `eyJhbGciOiJIUzI1...`
3. Open the `.env` file in your project folder (`d:\training\demo project\.env`) and paste them:

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here
```

---

## 🚀 How to Run the App Live

### Option A: Using Built-in Python Server (1-Click Run)
```bash
python backend/server.py
```
Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your browser!

### Option B: Using FastAPI & Uvicorn
```bash
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Run server
python -m uvicorn backend.main:app --reload --port 8000
```
Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your browser!
