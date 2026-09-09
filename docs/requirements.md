# Devil's Advocate Panel - Product Requirements Document (PRD)

## 1. Product Overview
"Pitch your idea. Get grilled by AI investors who won't go easy on you."

Devil's Advocate Panel is a full-stack, stateful multi-agent system designed to stress-test startup business models, assumptions, unit economics, defensibility, and market timing before founders pitch to real investors.

## 2. Core Agents & Personas
1. **Skeptical VC Agent**:
   - Focus: Scalability, moat/defensibility, market traction, founder credibility, investment risks, 10x exit potential.
   - Tone: Direct, ruthless, unpersuaded by buzzwords, demands proof of defensibility.
2. **Financial Analyst Agent**:
   - Focus: Pricing models, unit economics, CAC/LTV dynamics, gross margins, cash burn rate, runway, break-even timelines.
   - Tone: Quantitative, rigorous, zero tolerance for hand-waving financial metrics.
3. **Market Realist Agent**:
   - Focus: Competitive landscape, incumbent response, customer switching costs, adoption barriers, regulatory headwinds, market timing.
   - Tone: Pragmatic, grounded in actual market realities and historical startup failure patterns.

## 3. Workflow & Round Strategy
- **Standard Session**: 3 interactive rounds of interrogation.
- **Round 1 (Initial Stress Test)**: Each agent independently challenges the core premise and unverified assumptions of the pitch.
- **Round 2 (Deeper Interrogation)**: Agents react directly to the founder's initial rebuttal, targeting inconsistencies, evasions, or weak claims.
- **Round 3 (Final Defense)**: Agents push on the remaining existential risk or ask for ultimate proof/mitigation strategy.
- **Final Verdict Engine**: Once 3 rounds conclude, a comprehensive investment verdict report is synthesized, ranking weaknesses by severity (Critical / High / Medium / Low) with tactical fix recommendations and persona scores.

## 4. Reasoning Display Architecture
- Agents formulate user-facing, structured reasoning summaries rather than exposing internal raw chain-of-thought.
- Every challenge card displays:
  1. Specialist Persona & Bias
  2. Concise Reasoning Summary (why the agent is skeptical)
  3. Evidentiary citation / RAG benchmark
  4. Targeted Interrogation Question
  5. Weakness Severity Rating (Critical / High / Medium / Low)

## 5. Domain Knowledge & Multi-Agent RAG Scope
- Domain knowledge corpus categorized into:
  - `knowledge/business/`: Startup failure case studies, moat frameworks, network effects.
  - `knowledge/finance/`: SaaS benchmark metrics, marketplace unit economics, hardware margin realities.
  - `knowledge/market/`: Market sizing methodologies, distribution channel dynamics, adoption curves.
  - `knowledge/competition/`: Incumbent retaliation tactics, platform risk, regulatory hurdles.
- Vector Store: ChromaDB / FAISS semantic retrieval with metadata filtering per agent domain.

## 6. Persistence & Session Resumption
- MongoDB persistence (`devils_advocate` database) for sessions, state checkpoints, conversation transcripts, and verdict outputs.
- Sessions can be paused, resumed, and refreshed seamlessly without data loss.

## 7. Interfaces & Export
- **Frontend**: Next.js (App Router), TypeScript, responsive dark glassmorphism design with real-time round progress, animated persona cards, reasoning accordions, and interactive verdict dashboards.
- **Backend**: FastAPI REST API on port `8999` exposing session management, state streaming, resuming, and verdict generation.
- **PDF Export**: ReportLab PDF generator rendering executive investment-grade diagnostic reports with full round transcripts and severity breakdowns.
