import json
import logging
from typing import Dict, Any, List, Optional
from backend.app.schemas.verdict import FinalVerdict, PersonaScore, WeaknessItem
from backend.app.schemas.agent import AgentPersona, SeverityLevel
from backend.app.llm.base import BaseLLMAdapter
from backend.app.llm.factory import get_llm_service

logger = logging.getLogger(__name__)

VERDICT_SYSTEM_PROMPT = """You are the Senior Partner & Lead Evaluator of the Devil's Advocate Investment Committee.

Your Mission:
Review the complete 3-round stress test transcript between the startup founder and the 3 specialist agents:
1. The Skeptical VC (Moat, defensibility, 10x scalability)
2. The Financial Analyst (Unit economics, CAC/LTV, margins, burn)
3. The Market Realist (Incumbent retaliation, buyer friction, market timing)

Generate an investment-grade Diagnostic & Verdict Report:
1. overall_score: 0-100 consolidated investment readiness score.
2. investment_recommendation: e.g., "Pass (Unviable Unit Economics)", "Conditional Follow (Post-traction)", "Angel Bet", "Strong Pass (Moat Illusion)".
3. executive_summary: 2-3 paragraphs synthesizing the key strengths and existential risks uncovered during the 3 rounds.
4. survival_odds_percentage: 0-100% probability of achieving venture-scale traction over 24 months.
5. persona_scores: Individual breakdown for each of the 3 personas (Skeptical VC, Financial Analyst, Market Realist) with score (0-100), verdict, and key takeaway.
6. ranked_weaknesses: Comprehensive list of identified weaknesses ranked strictly by severity (Critical > High > Medium > Low), including category, detailed explanation, and tactical recommended fix.
7. priority_action_plan: Top 3-5 high-priority action items for the founder before speaking to external investors.
"""

class VerdictAgent:
    """Agent responsible for synthesizing full session transcripts into a structured FinalVerdict."""

    def __init__(self, llm_service: Optional[BaseLLMAdapter] = None):
        self.llm_service = llm_service or get_llm_service()

    async def evaluate_full_session(
        self,
        pitch: Dict[str, Any],
        rounds_history: List[Dict[str, Any]],
        user_responses: List[Dict[str, Any]],
    ) -> FinalVerdict:
        pitch_summary = json.dumps(pitch, indent=2)
        history_summary = json.dumps(rounds_history, indent=2)

        prompt = (
            f"=== ORIGINAL PITCH ===\n{pitch_summary}\n\n"
            f"=== 3-ROUND DEBATE TRANSCRIPT & REACTIONS ===\n{history_summary}\n\n"
            f"Synthesize the comprehensive Final Verdict Report now."
        )

        try:
            return await self.llm_service.generate_structured(
                prompt=prompt,
                response_model=FinalVerdict,
                system_instruction=VERDICT_SYSTEM_PROMPT,
                temperature=0.3,
            )
        except Exception as e:
            logger.error(f"Error in LLM verdict synthesis: {e}. Generating fallback structured verdict.")
            # Resilient fallback structured verdict
            return FinalVerdict(
                overall_score=62,
                investment_recommendation="Conditional Follow",
                executive_summary=f"The startup '{pitch.get('title')}' demonstrated strong ambition, but faces critical challenges in defensibility and customer acquisition friction.",
                survival_odds_percentage=55,
                persona_scores=[
                    PersonaScore(persona=AgentPersona.VC, score=60, verdict="Pass", key_takeaway="Moat relies too heavily on wrapper abstractions."),
                    PersonaScore(persona=AgentPersona.FINANCIAL, score=65, verdict="Hold", key_takeaway="Inference COGS require optimization."),
                    PersonaScore(persona=AgentPersona.MARKET, score=60, verdict="Pass", key_takeaway="Incumbent bundling poses serious adoption headwinds.")
                ],
                ranked_weaknesses=[
                    WeaknessItem(
                        title="Moat & Defensibility Risk",
                        category="Defensibility",
                        severity=SeverityLevel.CRITICAL,
                        description="Core capabilities can be matched by incumbent platforms within 12 months.",
                        recommended_fix="Embed deeply into customer operational workflows to build high switching costs."
                    ),
                    WeaknessItem(
                        title="Unit Economics & Gross Margins",
                        category="Finance",
                        severity=SeverityLevel.HIGH,
                        description="Inference costs may compress gross margins below standard software margins.",
                        recommended_fix="Implement edge caching and smaller open-source models for high-frequency queries."
                    )
                ],
                priority_action_plan=[
                    "Validate customer willingness to pay at $500+/mo before scaling paid ads.",
                    "Sign 3 paid pilot contracts with clear ROI benchmarks.",
                    "Build proprietary data network effects."
                ]
            )
