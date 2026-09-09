import asyncio
import logging
from typing import List, Dict, Any
from backend.app.evaluation.datasets import EVALUATION_DATASETS
from backend.app.evaluation.evaluators import (
    QuestionRelevanceEvaluator,
    PersonaConsistencyEvaluator,
    RAGGroundingEvaluator,
    EvaluatorResult,
)
from backend.app.agents.vc_agent import SkepticalVCAgent
from backend.app.agents.financial_agent import FinancialAnalystAgent
from backend.app.agents.market_agent import MarketRealistAgent
from backend.app.rag.service import rag_service

logger = logging.getLogger(__name__)

class EvaluationRunner:
    """Runs automated evaluation suite against benchmark datasets."""

    def __init__(self):
        self.vc = SkepticalVCAgent()
        self.fin = FinancialAnalystAgent()
        self.mkt = MarketRealistAgent()

    async def run_benchmark_evaluations(self) -> List[Dict[str, Any]]:
        results = []
        for dataset in EVALUATION_DATASETS:
            pitch = dataset["pitch"]
            rag_contexts = await rag_service.get_contexts_for_pitch(pitch)

            # Generate challenges
            ch_vc = await self.vc.generate_challenge(pitch, 1, rag_contexts.get("vc", ""), [])
            ch_fin = await self.fin.generate_challenge(pitch, 1, rag_contexts.get("financial", ""), [])
            ch_mkt = await self.mkt.generate_challenge(pitch, 1, rag_contexts.get("market", ""), [])

            # Evaluate each
            for ch, agent_name in [(ch_vc, "vc"), (ch_fin, "financial"), (ch_mkt, "market")]:
                ev_rel = QuestionRelevanceEvaluator.evaluate(pitch, ch)
                ev_per = PersonaConsistencyEvaluator.evaluate(ch)
                ev_rag = RAGGroundingEvaluator.evaluate(ch, rag_contexts.get(agent_name, ""))

                results.append({
                    "dataset_id": dataset["id"],
                    "category": dataset["category"],
                    "persona": ch.persona.value,
                    "question": ch.question,
                    "metrics": {
                        ev_rel.key: ev_rel.score,
                        ev_per.key: ev_per.score,
                        ev_rag.key: ev_rag.score,
                    }
                })

        logger.info(f"Completed evaluation run over {len(results)} agent challenges.")
        return results

eval_runner = EvaluationRunner()
