"""LangSmith Evaluation Datasets across diverse startup archetypes."""
from typing import List, Dict, Any

EVALUATION_DATASETS: List[Dict[str, Any]] = [
    {
        "id": "eval_ai_infra_01",
        "category": "AI Infrastructure",
        "pitch": {
            "title": "HyperTensor",
            "tagline": "Dynamic KV-Cache compression for LLM clusters",
            "problem": "LLM long-context inference runs out of HBM memory, causing severe latency spikes.",
            "solution": "Dynamic quantization and attention pruning that cuts KV cache memory by 75% without quality degradation.",
            "target_market": "Cloud GPU hosters and fine-tuning platforms.",
            "business_model": "Open-core + enterprise license ($2,000/GPU node/year).",
            "traction": "45 GitHub stars, 2 benchmark test runs.",
            "competition": "vLLM, FlashAttention, vLLM PagedAttention"
        },
        "expected_risk_categories": ["Defensibility / Moat", "OSS Substitution Risk"]
    },
    {
        "id": "eval_fintech_b2b_02",
        "category": "B2B FinTech",
        "pitch": {
            "title": "LedgerSync",
            "tagline": "Automated cross-border treasury reconciliation for Latin American SMBs",
            "problem": "Cross-border FX and localized tax reporting in LATAM requires 20+ manual accountant hours per month.",
            "solution": "Direct API integration into regional central banks and ERPs with automated tax remittance.",
            "target_market": "50,000 cross-border exporters across Mexico, Colombia, and Brazil.",
            "business_model": "0.35% transaction fee + $199/month SaaS subscription.",
            "traction": "$18k MRR growing 15% MoM.",
            "competition": "Manual spreadsheets, legacy regional banks"
        },
        "expected_risk_categories": ["Regulatory Compliance", "FX Volatility & Credit Risk"]
    },
    {
        "id": "eval_d2c_hardware_03",
        "category": "Hardware / Consumer",
        "pitch": {
            "title": "AeroBreathe",
            "tagline": "Personal AI-powered wearable air purification monitor",
            "problem": "Urban pollution causes chronic respiratory fatigue.",
            "solution": "Compact collar device with micro-sensors and localized HEPA filtration.",
            "target_market": "Metro city commuters in APAC.",
            "business_model": "$249 device + $29/quarter replacement filter subscription.",
            "traction": "Kickstarter funded ($80k raised).",
            "competition": "Dyson Zone, standard N95 masks"
        },
        "expected_risk_categories": ["Hardware Margins / COGS", "Supply Chain & Working Capital"]
    }
]
