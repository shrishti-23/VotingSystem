/* ==========================================================================
   Voting System - 100% Dynamic Client App Script (Resilient)
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  // Determine API base URL dynamically
  // const hostname = window.location.hostname || '127.0.0.1';
  // let API_BASE = (window.location.port === '8000') ? '/api' : `http://${hostname}:8000/api`;
  const hostname = window.location.hostname;

  let API_BASE;

  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    API_BASE = 'http://127.0.0.1:8000/api';
  } else {
    API_BASE = 'https://voting-by2k.onrender.com';
  }

  const candidatesGrid = document.getElementById('candidatesGrid');
  const totalVotesCount = document.getElementById('totalVotesCount');
  const leadingTechName = document.getElementById('leadingTechName');
  const dbStatusPill = document.getElementById('dbStatusPill');
  const dbStatusText = document.getElementById('dbStatusText');
  const btnTheme = document.getElementById('btnTheme');
  const toast = document.getElementById('toast');

  let candidates = [];

  // Theme Handler
  let theme = localStorage.getItem('voting_theme') || 'dark';
  document.documentElement.setAttribute('data-theme', theme);

  btnTheme.addEventListener('click', () => {
    theme = theme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('voting_theme', theme);
  });

  // Check API & Supabase Connection Status
  async function checkStatus() {
    try {
      const res = await fetch(`${API_BASE}/status`, { mode: 'cors' });
      const data = await res.json();

      if (data.is_supabase_connected) {
        dbStatusText.textContent = "Supabase PostgreSQL Connected";
        dbStatusPill.style.background = "rgba(16, 185, 129, 0.15)";
        dbStatusPill.style.color = "#10b981";
      } else {
        dbStatusText.textContent = "Supabase Disconnected";
        dbStatusPill.style.background = "rgba(244, 63, 94, 0.15)";
        dbStatusPill.style.color = "#f43f5e";
      }
    } catch (err) {
      console.warn("Status check error on primary API_BASE:", err);
      // Fallback try localhost if 127.0.0.1 failed
      if (API_BASE.includes('127.0.0.1')) {
        API_BASE = 'http://localhost:8000/api';
        try {
          const res2 = await fetch(`${API_BASE}/status`, { mode: 'cors' });
          const data2 = await res2.json();
          if (data2.is_supabase_connected) {
            dbStatusText.textContent = "Supabase PostgreSQL Connected";
            dbStatusPill.style.background = "rgba(16, 185, 129, 0.15)";
            dbStatusPill.style.color = "#10b981";
            return;
          }
        } catch (e2) {}
      }
      dbStatusText.textContent = "API Server Offline";
      dbStatusPill.style.background = "rgba(244, 63, 94, 0.15)";
      dbStatusPill.style.color = "#f43f5e";
    }
  }

  // Fetch 100% Dynamic Candidates from FastAPI & Supabase
  async function loadCandidates() {
    try {
      candidatesGrid.innerHTML = `<div class="loading">⏳ Fetching live data from Supabase PostgreSQL Database...</div>`;
      
      let res;
      try {
        res = await fetch(`${API_BASE}/candidates`, { mode: 'cors' });
      } catch (firstErr) {
        // Fallback to localhost if 127.0.0.1 failed
        console.warn("127.0.0.1 fetch failed, trying localhost...", firstErr);
        API_BASE = 'http://localhost:8000/api';
        res = await fetch(`${API_BASE}/candidates`, { mode: 'cors' });
      }

      if (!res.ok) {
        throw new Error(`HTTP Error Status: ${res.status}`);
      }

      candidates = await res.json();

      if (Array.isArray(candidates) && candidates.length > 0) {
        renderPoll();
      } else {
        candidatesGrid.innerHTML = `
          <div class="loading">
            ⚠️ Candidates table in Supabase PostgreSQL is empty.<br>
            <button class="vote-btn" style="width:auto; margin:1rem auto;" onclick="loadCandidates()">🔄 Retry Fetching</button>
          </div>`;
      }
    } catch (err) {
      console.error("loadCandidates Error:", err);
      candidatesGrid.innerHTML = `
        <div class="loading" style="color: #f43f5e;">
          ❌ Could not connect to Python FastAPI Backend at <strong>http://127.0.0.1:8000</strong>.<br>
          <small style="color:var(--text-dim); display:block; margin-top:0.5rem;">Error: ${escapeHtml(err.message || String(err))}</small>
          <button class="vote-btn" style="width:auto; margin:1rem auto;" onclick="loadCandidates()">🔄 Retry Connection</button>
        </div>`;
    }
  }

  // Render Poll Cards Dynamically
  function renderPoll() {
    if (!candidates || candidates.length === 0) return;

    const totalVotes = candidates.reduce((sum, c) => sum + (c.votes || 0), 0);
    totalVotesCount.textContent = totalVotes;

    const sorted = [...candidates].sort((a, b) => (b.votes || 0) - (a.votes || 0));
    leadingTechName.textContent = sorted[0] ? sorted[0].name : '-';

    candidatesGrid.innerHTML = candidates.map(c => {
      const votes = c.votes || 0;
      const percentage = totalVotes > 0 ? Math.round((votes / totalVotes) * 100) : 0;
      const icon = c.icon || '⚡';

      return `
        <div class="candidate-card">
          <div class="candidate-header">
            <div class="candidate-info">
              <div class="candidate-icon">${icon}</div>
              <div>
                <div class="candidate-name">${escapeHtml(c.name)}</div>
                <div class="candidate-category">${escapeHtml(c.category)}</div>
              </div>
            </div>
          </div>

          <div class="vote-bar-container">
            <div class="bar-labels">
              <span>${votes} Votes</span>
              <span>${percentage}%</span>
            </div>
            <div class="progress-track">
              <div class="progress-fill" style="width: ${percentage}%"></div>
            </div>
          </div>

          <button class="vote-btn" onclick="castVote('${c.id}')">
            🗳️ Vote for ${escapeHtml(c.name)}
          </button>
        </div>
      `;
    }).join('');
  }

  // Cast Vote Callback: Calls Backend API -> Updates Supabase -> Re-fetches database
  window.castVote = async function(candidateId) {
    try {
      showToast("Submitting vote to Supabase Database...");
      const res = await fetch(`${API_BASE}/vote/${candidateId}`, { method: 'POST', mode: 'cors' });
      const data = await res.json();

      if (res.ok) {
        showToast(`Vote saved in Supabase for ${data.candidate.name}! 🎉`);
        // Re-fetch 100% live data from database
        loadCandidates();
      } else {
        alert("Failed to update database: " + (data.detail || "Unknown error"));
      }
    } catch (err) {
      alert("Network error. Ensure Python Backend is running on port 8000.");
    }
  };

  function showToast(msg) {
    toast.textContent = msg;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 2500);
  }

  function escapeHtml(str) {
    return str.replace(/[&<>"']/g, match => {
      const escape = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
      return escape[match];
    });
  }

  window.loadCandidates = loadCandidates;

  checkStatus();
  loadCandidates();
});
