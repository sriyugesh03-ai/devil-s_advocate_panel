# 🔄 Devil's Advocate Panel - Complete System Workflow

This document details the end-to-end execution workflow of the **Devil's Advocate Panel**, tracing the lifecycle of a startup pitch from initial intake to final investment memo generation.

---

## 🧭 Workflow High-Level Overview

```mermaid
sequenceDiagram
    autonumber
    actor Founder as 👤 Founder / User
    participant Frontend as 💻 Next.js 14 Web App
    participant Proxy as 🛡️ SSR Proxy (/api/proxy)
    participant API as ⚡ FastAPI Backend
    participant MCP as 🔌 MCP Tools (Tavily/GitHub/PDF)
    participant RAG as 📚 Vector Store (ChromaDB)
    participant Graph as 🤖 LangGraph Multi-Agent Engine
    participant LLM as 🧠 LLM (Groq 120B / Gemini)
    participant DB as 🗄️ MongoDB Atlas
    participant PDF as 📄 ReportLab PDF Generator

    %% Step 1: Ingestion
    Founder->>Frontend: Enter pitch details or upload Pitch Deck (.pdf)
    alt PDF Deck Uploaded
        Frontend->>Proxy: POST /api/pitches/parse-deck
        Proxy->>API: Forward PDF Multipart
        API->>MCP: PitchDeckParserTool.extract()
        MCP-->>Frontend: Auto-fill Form Fields
    end

    Founder->>Frontend: Submit Pitch Dossier
    Frontend->>Proxy: POST /api/pitches/
    Proxy->>API: Validate with StartupPitchCreate
    API->>DB: Save Pitch Record & Initialize Session
    API->>Graph: Initialize LangGraph State (Round 1)

    %% Step 2: Round 1 Execution
    par Agent Cross-Examination
        Graph->>RAG: Retrieve failure case studies & SaaS comps
        Graph->>MCP: Execute live Tavily competitor search & GitHub tech audit
        Graph->>LLM: Generate Skeptical VC Challenge
        Graph->>LLM: Generate Financial Analyst Challenge
        Graph->>LLM: Generate Market Realist Challenge
    end
    Graph->>DB: Checkpoint Round 1 State
    Graph-->>Frontend: Return 3 Agent Challenges (Status: await_user)

    %% Step 3: Human-in-the-loop Rounds
    loop Rounds 1 to 3
        Founder->>Frontend: Submit Counter-Defenses
        Frontend->>Proxy: POST /api/sessions/{id}/respond
        Proxy->>API: Resume LangGraph Execution
        Graph->>LLM: Evaluate Founder Defenses against RAG/MCP Evidence
        alt Current Round < 3
            Graph->>Graph: Increment Round & Formulate Harder Follow-ups
            Graph-->>Frontend: Return Next Round Challenges
        else Round 3 Completed
            Graph->>Graph: Transition to Verdict Arbiter Node
        end
    end

    %% Step 4: Verdict & PDF Memo
    Graph->>LLM: Generate Weighted Score (0-10) & Weakness Matrix
    Graph->>DB: Persist Final Verdict & Decision
    Graph-->>Frontend: Display Final Verdict Dashboard

    opt Founder requests PDF Memo
        Founder->>Frontend: Click "Download Investment Memo"
        Frontend->>API: GET /api/sessions/{id}/pdf
        API->>PDF: Generate Styled Institutional PDF
        PDF-->>Founder: Stream Investment Memo (.pdf)
    end
```

---

## 📋 Phase-by-Phase Workflow Breakdown

### 1. Ingestion & Pre-Diligence Phase
1. **User Action**: The founder fills out the pitch dossier or drops a `.pdf` pitch deck into the upload area.
2. **MCP Parsing**: If a PDF is uploaded, `PitchDeckParserTool` extracts slide text and prompts the LLM to structure problem, solution, TAM, business model, traction, and fundraising goal.
3. **Session Creation**: `POST /api/pitches/` creates a MongoDB session document with a unique `session_id` and round counter `current_round = 1`.

---

### 2. External Diligence & RAG Context Retrieval
Before agents generate questions:
- **Tavily MCP Search**: If enabled, searches for stealth competitors, alternative platforms, and pricing benchmarks.
- **GitHub MCP Audit**: If a repository URL is supplied and enabled, audits commit frequency, language distribution, and star count.
- **ChromaDB Semantic Retrieval**: Queries the local vector store for historical failure modes (e.g. Quibi's burn rate, Fast's CAC explosion) and standard SaaS metrics.

---

### 3. The 3-Round Interrogation Loop (LangGraph Crucible)

```mermaid
stateDiagram-v2
    [*] --> IngestPitch
    IngestPitch --> Round1_Interrogate: Initialize State
    
    state "Round 1: First Impressions" as Round1_Interrogate {
        VC_1: Skeptical VC Attacks Moat
        FA_1: Financial Analyst Attacks Margins
        MR_1: Market Realist Attacks TAM
    }
    
    Round1_Interrogate --> AwaitFounder_1: Interrupt before await_user
    AwaitFounder_1 --> EvaluateDefense_1: Founder Submits Round 1 Answers
    
    EvaluateDefense_1 --> Round2_Interrogate: Round Counter = 2
    
    state "Round 2: Deep Cross-Examination" as Round2_Interrogate {
        VC_2: Challenge Founder Claims
        FA_2: Probe Unit Economics & Payback
        MR_2: Scrutinize Competitive Differentiation
    }
    
    Round2_Interrogate --> AwaitFounder_2: Interrupt before await_user
    AwaitFounder_2 --> EvaluateDefense_2: Founder Submits Round 2 Answers
    
    EvaluateDefense_2 --> Round3_Interrogate: Round Counter = 3
    
    state "Round 3: Fatal Stress-Test" as Round3_Interrogate {
        VC_3: Final Moat & Defensibility Test
        FA_3: Runway, Burn Multiple & Liquidity Test
        MR_3: Incumbent Retaliation & Platform Risk
    }
    
    Round3_Interrogate --> AwaitFounder_3: Interrupt before await_user
    AwaitFounder_3 --> EvaluateDefense_3: Founder Submits Round 3 Answers
    
    EvaluateDefense_3 --> VerdictArbiter: All 3 Rounds Complete
    VerdictArbiter --> GeneratePDF: Compute 5-Pillar Score
    GeneratePDF --> [*]: Session Completed
```

---

### 4. Verdict Arbiter & Multi-Criteria Scoring

The **Verdict Arbiter** analyzes the entire 3-round dialogue transcript and calculates a 0–10 score based on 5 weighted pillars:

| Evaluation Pillar | Weight | Description |
| :--- | :---: | :--- |
| **Market Viability & TAM** | **25%** | Realistic serviceable market vs. inflated top-down TAM. |
| **Moat & Defensibility** | **25%** | Technical barrier, proprietary IP, switching costs, and network effects. |
| **Unit Economics & Business Model** | **25%** | Gross margin profile, LTV/CAC ratio, payback velocity, and pricing power. |
| **Execution Agility & Founder Clarity** | **15%** | Quality of defenses, intellectual honesty, and responsiveness under pressure. |
| **Timing & Scalability** | **10%** | Market timing tailwinds and capital efficiency at scale. |

#### Categorical Investment Decisions
- **`STRONG_INVEST`** (Score $\ge 8.5$): Exceptional defensibility, scalable unit economics, and rock-solid market timing.
- **`LEAN_INVEST`** (Score $7.0 - 8.4$): Promising business model with minor operational or market risks.
- **`MORE_DATA`** (Score $5.5 - 6.9$): Unproven assumptions requiring customer validation and pilot data.
- **`PASS`** (Score $4.0 - 5.4$): Significant structural flaws, weak moat, or unsustainable CAC.
- **`HARD_PASS`** (Score $< 4.0$): Fatal unit economics, direct incumbent commoditization, or regulatory blockers.

---

### 5. Institutional PDF Memo Export

The backend `PDFReportGenerator` ([backend/app/pdf/generator.py](file:///d:/projects/devil's_advocate_panel/backend/app/pdf/generator.py)) compiles an executive ReportLab PDF featuring:
- Executive Summary & Company Metadata.
- Final Investment Decision Banner with color-coded score gauge.
- 5-Pillar Evaluation Score Breakdown Table.
- Prioritized Weakness Matrix (categorized by `HIGH`, `MEDIUM`, and `LOW` severity).
- Actionable Strategic Pivot & De-risking Roadmap.
- Complete 3-Round Cross-Examination Dialogue Transcripts.
