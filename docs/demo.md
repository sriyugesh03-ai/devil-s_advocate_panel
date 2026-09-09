# Devil's Advocate Panel - Demo Walkthrough & Script

## 🎯 Demo Concept
"Pitch your idea. Get grilled by AI investors who won't go easy on you."

## 🚀 Live Demo Walkthrough (3-Minute Script)

### Step 1: Landing Page & Persona Introduction (0:00 - 0:30)
1. Open [http://localhost:3000](http://localhost:3000).
2. Highlight the 3 adversarial personas:
   - **The Skeptical VC**: Defensibility, Moats, 10x Scale, Exit Multiples.
   - **The Financial Analyst**: CAC/LTV, Burn Rate, Inference COGS, Margins.
   - **The Market Realist**: Incumbent Bundling, Buyer Inertia, GTM Timing.
3. Click **"Enter the Panel"**.

### Step 2: Pitch Submission (0:30 - 1:00)
1. Pre-filled demo pitch: **PulseShield AI** (Autonomous AI Reliability & Chaos Engineering for Enterprise Microservices).
2. Click **"Begin Interrogation (Round 1)"**.
3. Point out how FastAPI, LangGraph, and RAG orchestrate in parallel to formulate targeted challenges.

### Step 3: Round 1 to Round 3 Gauntlet (1:00 - 2:00)
1. **Round 1**: Expand the *Agent Reasoning & Thesis Skepticism* accordion to show the user-facing reasoning summaries and cited Hamilton Helmer 7-Powers benchmarks.
2. Enter rebuttal:
   > *"We integrate directly at the Linux kernel level via eBPF, giving us 10x deeper visibility than Datadog, with an open-source community providing zero-CAC inbound leads."*
3. Submit rebuttal: Observe dynamic follow-up pressure in Round 2.
4. Complete Round 3.

### Step 4: Final Investment Verdict & PDF Export (2:00 - 3:00)
1. View the **Consolidated Investment Score** and **24-Month Survival Odds**.
2. Examine the **Weakness Ranking** with tactical recommended fixes for each severity level.
3. Click **"Download Executive PDF Report"** to open the ReportLab generated diagnostic report.

---

## 🛠️ Local Execution Commands

### 1. Start MongoDB (if using Docker)
```bash
docker run -d -p 27017:27017 --name devils_advocate_mongo mongo:7.0
```

### 2. Run Backend
```bash
# In ./backend
uvicorn backend.app.main:app --host 0.0.0.0 --port 8999 --reload
```

### 3. Run Frontend
```bash
# In ./frontend
npm run dev
```
