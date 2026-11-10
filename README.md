# CODEARENA X 🏆
### Multi-Language Coding Assessment, Automated Evaluation and Developer Analytics Platform

CODEARENA X is a full-stack coding assessment platform that allows administrators to create programming challenges, candidates to solve them using a Monaco Editor workspace, and provides real-time automated evaluation using Docker container isolation.

## 🚀 Features
- **Authentication & RBAC:** JWT-based login with Administrator, Assessment Manager, and Candidate roles.
- **Secure Execution Engine:** Runs Python, JavaScript, and C++ inside isolated Docker containers (`--network none`, read-only, non-root).
- **Automated Test Cases:** Evaluates public and hidden test cases with Time Limit and Memory Limit enforcement.
- **Real-Time Monitoring:** WebSocket integration for live submission status updates.
- **Timed Assessments:** Schedule exams with server-authoritative countdown timers.
- **Analytics Dashboard:** Visualizes platform statistics (language usage, failures) using Recharts.
- **Global Leaderboard:** Automatically ranks candidates based on challenge difficulty and accepted submissions.

## 🛠️ Tech Stack
- **Frontend:** React, Vite, TypeScript, Tailwind CSS, Monaco Editor, Recharts
- **Backend:** Python, FastAPI, SQLite, WebSockets, Pytest
- **Infrastructure:** Docker, Docker Compose

## 💻 How to Run Locally

### 1. Backend (FastAPI)
`cd backend`
`python -m venv .venv`
`pip install -r requirements.txt`
`uvicorn app.main:app --reload --port 8010`

### 2. Frontend (Vite)
`cd frontend`
`npm install`
`npm run dev`

### 3. Access the Platform
Open your browser to `http://localhost:5173`

**Default Credentials:**
- **Admin:** `admin@codearnax.dev` / `Admin1234`
- **Candidate:** `cand@codearnax.dev` / `Cand1234`
