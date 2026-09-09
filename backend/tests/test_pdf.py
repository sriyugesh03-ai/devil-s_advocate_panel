import pytest
import io
from backend.app.pdf.generator import PDFReportGenerator

def test_pdf_report_generation():
    generator = PDFReportGenerator()
    dummy_session = {
        "pitch": {
            "title": "QuantumFlow AI",
            "tagline": "Real-time AI pipeline acceleration",
            "business_model": "Usage-based software license",
            "problem": "High inference latency",
            "solution": "Kernel optimizations"
        },
        "verdict": {
            "overall_score": 75,
            "investment_recommendation": "Conditional Follow",
            "executive_summary": "Promising technology with market friction.",
            "survival_odds_percentage": 70,
            "persona_scores": [
                {"persona": "Skeptical VC", "score": 70, "verdict": "Pass", "key_takeaway": "Needs moat."},
                {"persona": "Financial Analyst", "score": 80, "verdict": "Invest", "key_takeaway": "Good margins."},
                {"persona": "Market Realist", "score": 75, "verdict": "Hold", "key_takeaway": "Long sales cycle."}
            ],
            "ranked_weaknesses": [
                {
                    "title": "OSS Commoditization",
                    "category": "Defensibility",
                    "severity": "Critical",
                    "description": "Risk of open-source frameworks copying the kernel.",
                    "recommended_fix": "Focus on proprietary workflow automation."
                }
            ],
            "priority_action_plan": ["Close enterprise pilots", "Benchmark against latest OSS"]
        },
        "rounds_history": [
            {
                "round_number": 1,
                "challenges": [
                    {
                        "persona": "Skeptical VC",
                        "severity": "Critical",
                        "reasoning_summary": "OSS moves fast.",
                        "question": "How do you protect your IP from OSS?"
                    }
                ],
                "founder_response": "We patent our kernel designs."
            }
        ]
    }

    pdf_buffer = generator.generate_report(dummy_session)
    assert isinstance(pdf_buffer, io.BytesIO)
    content = pdf_buffer.getvalue()
    assert len(content) > 1000  # valid PDF binary stream
    assert content.startswith(b"%PDF")
