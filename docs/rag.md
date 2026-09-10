# 📚 Retrieval-Augmented Generation (RAG) Engine

This document details the **Retrieval-Augmented Generation (RAG)** architecture, knowledge base structure, semantic retrieval pipeline, and prompt injection mechanisms utilized by the **Devil's Advocate Panel**.

---

## 🎯 Purpose of RAG in the Investment Gauntlet

Generic LLMs tend to produce polite, generic feedback. To simulate an elite venture capital panel, the agents must cite **empirical market facts, historical failure modes, and industry benchmark metrics**.

The RAG engine ensures that:
1. **The Skeptical VC** cites actual defensibility failures (e.g. Segway's lack of infrastructure, Theranos' unverified technical claims).
2. **The Financial Analyst** references SaaS benchmark metrics (e.g. magic number, CAC payback periods, gross margin thresholds) and compares unit economics to historical disasters (e.g. Fast's $17M burn rate on $600k revenue).
3. **The Market Realist** references real-world market miscalculations (e.g. Quibi's misreading of mobile short-form behavior vs. TikTok/YouTube).

---

## 🏗️ RAG Pipeline Architecture

```mermaid
flowchart TD
    subgraph DataIngestion ["1. Knowledge Ingestion & Pre-Processing"]
        RawFiles["Raw Knowledge Files<br/>(backend/knowledge/*.md)"]
        PostMortems["Startup Failure Post-Mortems<br/>(Quibi, Fast, WeWork, Theranos, Segway)"]
        SaaSBenchmarks["B2B / B2C SaaS Financial Benchmarks<br/>(CAC, LTV, Gross Margins, Magic Numbers)"]
        
        RawFiles --> PostMortems & SaaSBenchmarks
        PostMortems & SaaSBenchmarks --> Loader["Markdown / Text Loader<br/>(loaders.py)"]
        Loader --> Chunker["Semantic Header & Sentence Chunker<br/>(chunker.py)"]
    end

    subgraph EmbeddingStorage ["2. Embedding & Vector Indexing"]
        Embedder["Embedding Model<br/>(OpenAI text-embedding-3-small / Fallback Embedder)"]
        VectorDB[("ChromaDB Persistent Store<br/>(vector_store.py)")]
        
        Chunker -->|Text Chunks (500 tokens, 50 overlap)| Embedder
        Embedder -->|Dense Vectors (1536 dim)| VectorDB
    end

    subgraph RuntimeRetrieval ["3. Dynamic Query & Prompt Injection"]
        PitchInput["Startup Pitch Dossier / Round Topic"]
        QueryGen["Contextual Query Formulator"]
        Retriever["Cosine Similarity Top-K Retriever<br/>(retriever.py)"]
        
        PitchInput --> QueryGen
        QueryGen -->|Semantic Query| Retriever
        Retriever <-->|Vector Distance Search (k=3)| VectorDB
        
        Retriever --> ContextFormatter["Context Assembly & Formatting"]
        ContextFormatter --> AgentPrompts["Specialist Agent Prompts<br/>(VC, Financial, Market)"]
    end
```

---

## 📂 Knowledge Base Structure

The curated domain knowledge lives under `backend/knowledge/` and includes:

| Knowledge File | Domain | Key Insights & Failure Modes |
| :--- | :--- | :--- |
| `failures/quibi.md` | Consumer Tech / Media | Misreading mobile user behavior, refusing social sharing, spending $1.75B before product-market fit. |
| `failures/fast.md` | FinTech / Checkout | Spending $17M/mo with $600k ARR, subsidized merchant acquisition, unsustainable unit economics. |
| `failures/wework.md` | Real Estate Tech | Asset-liability duration mismatch, tech multiple on commodity lease business, governance collapse. |
| `failures/theranos.md` | HealthTech / DeepTech | Faking technical validation, regulatory evasion, inability to scale proprietary micro-fluidics. |
| `failures/segway.md` | Hardware / Mobility | High cost ($5,000), absence of urban infrastructure, consumer social friction. |
| `benchmarks/saas_metrics.md` | SaaS Finance | Enterprise CAC payback (< 12 mo), LTV/CAC (> 3x), Net Revenue Retention (> 110%), Gross Margins (> 75%). |
| `benchmarks/marketplace.md` | Marketplaces | Take rates (10–25%), two-sided liquidity thresholds, multi-tenant disintermediation risks. |

---

## ⚙️ Core Pipeline Components

### 1. Document Chunking ([backend/app/rag/chunker.py](file:///d:/projects/devil's_advocate_panel/backend/app/rag/chunker.py))
- **Strategy**: Markdown Section-Aware Chunking.
- **Chunk Size**: $\approx 500$ tokens with a 50-token sliding overlap.
- **Metadata Tagging**: Each chunk is tagged with `source_document`, `category` (e.g. `failure_case_study`, `benchmark`), and `key_metrics`.

### 2. Embeddings & Vector Store ([backend/app/rag/vector_store.py](file:///d:/projects/devil's_advocate_panel/backend/app/rag/vector_store.py))
- **Primary Engine**: **ChromaDB** in-process vector store.
- **Embedding Function**: OpenAI `text-embedding-3-small` with high-performance localized caching.
- **Fallback Embedder**: Deterministic TF-IDF feature hashing for zero-dependency offline resilience.

### 3. Semantic Retrieval ([backend/app/rag/retriever.py](file:///d:/projects/devil's_advocate_panel/backend/app/rag/retriever.py))
- **Query Construction**: Combines the startup's `problem`, `solution`, `business_model`, and `target_market`.
- **Similarity Metric**: Cosine Distance.
- **Top-K Selection**: Ingests top $k=3$ most semantically relevant failure modes and metric comp sheets per agent turn.

---

## 💉 Agent Prompt Injection Example

When the **Financial Analyst Agent** executes Round 1, the retrieved RAG context is injected directly into the system prompt:

```markdown
=== RETRIEVED DOMAIN KNOWLEDGE & BENCHMARKS ===
[SOURCE: SaaS Financial Benchmarks 2024]
- Top quartile B2B Enterprise SaaS gross margins: 78% - 85%.
- Target CAC Payback Period: < 12 months for Mid-Market, < 18 months for Enterprise.
- LTV/CAC below 3.0x indicates marketing inefficiency or high churn rate.

[SOURCE: Fast Checkout Post-Mortem]
- Fast burned through $102M in venture funding with an annualized revenue of only $600k.
- Fatal flaw: High fixed headcount costs with sub-scale transaction take rates (1.5%).
================================================
```

The agent uses this empirical context to directly challenge the founder's assumptions with specific benchmark comparisons.
