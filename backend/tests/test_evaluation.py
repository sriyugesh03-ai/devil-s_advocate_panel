import pytest
from backend.app.schemas.agent import AgentChallenge, AgentPersona, SeverityLevel
from backend.app.evaluation.evaluators import (
    QuestionRelevanceEvaluator,
    PersonaConsistencyEvaluator,
    RAGGroundingEvaluator
)

def test_evaluators_unit():
    pitch = {
        "title": "HyperTensor",
        "business_model": "$2,000/node/year",
        "solution": "Dynamic KV cache"
    }
    challenge = AgentChallenge(
        persona=AgentPersona.FINANCIAL,
        reasoning_summary="SaaS pricing with high cloud GPU burn requires 80%+ margins.",
        question="What is your gross margin per GPU node hour considering cloud host costs?",
        severity=SeverityLevel.HIGH,
        evidence_citation="SaaS Unit Economics Benchmark"
    )

    ev_rel = QuestionRelevanceEvaluator.evaluate(pitch, challenge)
    assert ev_rel.score >= 0.7

    ev_per = PersonaConsistencyEvaluator.evaluate(challenge)
    assert ev_per.score >= 0.5

    ev_rag = RAGGroundingEvaluator.evaluate(challenge, "SaaS Unit Economics")
    assert ev_rag.score == 1.0
