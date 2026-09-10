# 🦜 LangChain Integration & LLM Architecture

This document details how **LangChain** primitives, prompt engineering, structured output parsing, and multi-provider LLM adapters are implemented in the **Devil's Advocate Panel**.

---

## 🎯 LangChain Integration Highlights

The platform utilizes LangChain for:
1. **Multi-Provider LLM Abstraction**: Unified interface switching dynamically between **Groq** (`openai/gpt-oss-120b`) and **Google Gemini** (`gemini-2.5-flash`).
2. **Prompt Engineering & System Personas**: Templatized system prompts injecting pitch parameters, historical RAG evidence, and live MCP intelligence.
3. **Structured Pydantic Output Parsing**: Enforcing strict JSON schema outputs for agent challenges, severity ratings, scores, and PDF memo structures.
4. **Resilience & Observability**: Automatic exponential backoff retries and optional **LangSmith** tracing.

---

## 🏗️ LLM Adapter Architecture

```mermaid
flowchart TD
    subgraph AgentCallers ["Agent Callers"]
        VCAgent["Skeptical VC"]
        FinAgent["Financial Analyst"]
        MktAgent["Market Realist"]
        VerdAgent["Verdict Arbiter"]
    end

    subgraph LLMFactoryLayer ["LLM Factory & Base Interface (app/llm/)"]
        Factory["LLMFactory.get_adapter()"]
        BaseAdapter["BaseLLMAdapter (Abstract Base Class)"]
    end

    subgraph Adapters ["Provider Adapters"]
        GroqAdapter["GroqLLMAdapter<br/>(openai/gpt-oss-120b)"]
        GeminiAdapter["GeminiLLMAdapter<br/>(gemini-2.5-flash)"]
    end

    subgraph ExternalAPIs ["Cloud LLM APIs"]
        GroqAPI["Groq Cloud API<br/>(500 tokens/sec)"]
        GeminiAPI["Google AI Studio API"]
    end

    AgentCallers --> Factory
    Factory --> BaseAdapter
    BaseAdapter --> GroqAdapter & GeminiAdapter
    GroqAdapter -->|Primary (Free-tier 120B)| GroqAPI
    GeminiAdapter -->|Fallback / Multimodal| GeminiAPI
```

---

## 🎭 Persona Prompt Engineering

Each agent is defined with a dedicated system prompt in [backend/app/agents/](file:///d:/projects/devil's_advocate_panel/backend/app/agents/):

### 1. The Skeptical VC Prompt (`vc_agent.py`)
```markdown
You are Alex Vance, a veteran General Partner at a Tier-1 venture fund with $2B AUM.
Your role is to destroy weak assumptions around MOATS, DEFENSIBILITY, NETWORK EFFECTS, and TECHNICAL FEASIBILITY.
- Tone: Razor-sharp, skeptical, impatient, highly analytical.
- Never accept hand-wavy claims like "first-mover advantage" or "our AI is smarter".
- Cite real competitors and historical failures from the provided context.
```

### 2. The Financial Analyst Prompt (`financial_agent.py`)
```markdown
You are Marcus Chen, a ruthless Principal focusing on unit economics, capital efficiency, and SaaS benchmarks.
Your role is to dissect CAC, LTV, gross margins, payback periods, burn multiples, and pricing models.
- Tone: Quantitative, relentless, metric-driven.
- Compare founder projections against standard industry benchmarks.
- Calculate implied burn rates and highlight cash runway traps.
```

### 3. The Market Realist Prompt (`market_agent.py`)
```markdown
You are Elena Rostova, an ex-operator and venture partner specializing in go-to-market dynamics and regulatory risk.
Your role is to challenge TAM validity, platform risk, customer acquisition bottlenecks, and incumbent retaliation.
- Tone: Pragmatic, street-smart, macro-aware.
- Highlight channel conflict, distribution moats, and buyer inertia.
```

---

## 📑 Structured Output Enforcement

Agents return strictly validated JSON matching Pydantic schemas ([backend/app/schemas/agent.py](file:///d:/projects/devil's_advocate_panel/backend/app/schemas/agent.py)):

```python
from pydantic import BaseModel, Field
from typing import List, Literal

class AgentChallenge(BaseModel):
    agent_name: str
    persona: Literal["Skeptical VC", "Financial Analyst", "Market Realist"]
    round: int
    challenge_title: str = Field(description="Concise 5-8 word punchy challenge title")
    critique: str = Field(description="Detailed 2-3 paragraph brutal cross-examination")
    cited_precedents: List[str] = Field(description="Historical failure case studies or SaaS benchmarks cited")
    severity: Literal["HIGH", "MEDIUM", "LOW"]
    probing_question: str = Field(description="Single, high-stakes question the founder must answer")
```

---

## 📊 Model Strategy & Selection

| Provider | Model Name | Latency | Context Window | Role |
| :--- | :--- | :---: | :---: | :--- |
| **Groq** | `openai/gpt-oss-120b` | **~2.1s** | 128k | **Default Primary**: High reasoning power and instantaneous generation speeds. |
| **Google** | `gemini-2.5-flash` | **~3.4s** | 1M | **Fallback / Multimodal**: Long-context reasoning and backup redundancy. |

---

## 🔍 LangSmith Observability

When `LANGSMITH_TRACING=true` is enabled in `.env`:
- Every agent invocation, tool execution, and prompt token count is streamed to **LangSmith**.
- Tracks token consumption, latency bottlenecks, and output validation errors in real time.
