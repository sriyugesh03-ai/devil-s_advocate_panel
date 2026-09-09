# Architecture Decision Records (ADR) - Devil's Advocate Panel

## ADR 001: Multi-Agent Orchestration via LangGraph
- **Context**: The application requires stateful multi-round conversations, parallel execution of multiple specialist agents per round, dynamic routing, and human-in-the-loop pauses.
- **Decision**: Use LangGraph with state channels and checkpoints.
- **Consequences**: Enables deterministic state tracking, easy rollback/resumption, and independent agent execution branches that merge into a consolidated round state.

## ADR 002: Model Provider Agnostic LLM Gateway
- **Context**: The system must support both Google Gemini (e.g. `gemini-2.5-flash`, `gemini-1.5-pro`) and Groq (e.g. `openai/gpt-oss 120b`, `llama-3.3-70b-versatile`) with structured JSON outputs.
- **Decision**: Build a unified adapter interface (`LLMService`) with provider factories, automatic retries, timeout handling, and fallback resilience.
- **Consequences**: Eliminates vendor lock-in and allows seamless switching between high-speed inference (Groq) and rich reasoning (Gemini).

## ADR 003: Database Persistence using MongoDB
- **Context**: Session state, round transcripts, agent evaluations, and user responses require flexible document storage with fast asynchronous querying and persistence across page refreshes.
- **Decision**: Use MongoDB with Motor / PyMongo for async document persistence alongside LangGraph checkpointing.
- **Consequences**: Reliable persistence, flexible schema evolution for dynamic multi-agent rounds, and high performance.

## ADR 004: Domain Knowledge Retrieval (Agent-Specific RAG)
- **Context**: General LLMs can hallucinate standard investor benchmarks or give overly generic critiques.
- **Decision**: Ground each agent with domain-specific knowledge bases (`business`, `finance`, `market`, `competition`) using vector embeddings and metadata filtering.
- **Consequences**: The Skeptical VC cites real moat frameworks; the Financial Analyst cites standard SaaS/marketplace ratios; the Market Realist references real failure modes and adoption friction.

## ADR 005: User-Facing Reasoning Summaries
- **Context**: Hidden chain-of-thought isn't accessible to users, but founders need to understand *why* the panel is challenging them.
- **Decision**: Explicitly separate internal deliberation into a structured `reasoning_summary` field displayed to the user alongside the sharp challenge question.
- **Consequences**: Improves transparency and educational value without cluttering the UI with unformatted raw logs.

## ADR 006: Port Configuration
- **Context**: Port 8000 is occupied by other local services.
- **Decision**: Run FastAPI backend on port `8999` and configure Next.js frontend to proxy/call `http://localhost:8999`.
