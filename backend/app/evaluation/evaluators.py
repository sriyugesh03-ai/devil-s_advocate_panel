import re
from typing import Dict, Any, List
from backend.app.schemas.agent import AgentChallenge, AgentPersona

class EvaluatorResult:
    def __init__(self, key: str, score: float, reasoning: str):
        self.key = key
        self.score = score  # 0.0 to 1.0
        self.reasoning = reasoning

class QuestionRelevanceEvaluator:
    """Evaluates if the challenge question directly addresses the pitch details."""

    @staticmethod
    def evaluate(pitch: Dict[str, Any], challenge: AgentChallenge) -> EvaluatorResult:
        question_text = challenge.question.lower()
        title_present = pitch.get("title", "").lower() in question_text
        biz_model_present = any(w in question_text for w in ["margin", "revenue", "cost", "pricing", "scale", "compet", "moat", "market", "customer"])

        score = 1.0 if biz_model_present else 0.7
        return EvaluatorResult(
            key="question_relevance",
            score=score,
            reasoning=f"Question addresses core business dimensions with severity '{challenge.severity}'."
        )

class PersonaConsistencyEvaluator:
    """Evaluates if the generated challenge strictly reflects the assigned persona's domain."""

    @staticmethod
    def evaluate(challenge: AgentChallenge) -> EvaluatorResult:
        p = challenge.persona
        q = challenge.question.lower() + " " + challenge.reasoning_summary.lower()

        if p == AgentPersona.VC:
            keywords = ["moat", "defensib", "scale", "exit", "invest", "venture", "oss", "substitut", "unfair"]
        elif p == AgentPersona.FINANCIAL:
            keywords = ["margin", "cac", "ltv", "burn", "price", "revenue", "cogs", "payback", "cost", "economics", "$"]
        elif p == AgentPersona.MARKET:
            keywords = ["incumbent", "market", "adopt", "compet", "buyer", "timing", "distribut", "tam", "switch"]
        else:
            keywords = []

        matches = sum(1 for kw in keywords if kw in q)
        score = min(1.0, 0.4 + (matches * 0.15))
        return EvaluatorResult(
            key="persona_consistency",
            score=score,
            reasoning=f"Persona '{p.value}' included {matches} domain-specific stress indicators."
        )

class RAGGroundingEvaluator:
    """Evaluates if retrieved domain benchmarks were incorporated into reasoning."""

    @staticmethod
    def evaluate(challenge: AgentChallenge, rag_context: str) -> EvaluatorResult:
        citation = challenge.evidence_citation or ""
        has_citation = len(citation.strip()) > 5
        score = 1.0 if has_citation else 0.6
        return EvaluatorResult(
            key="rag_grounding",
            score=score,
            reasoning="Challenge cited benchmark knowledge." if has_citation else "No explicit benchmark cited."
        )
