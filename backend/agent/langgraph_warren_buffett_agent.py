"""
LangGraph-powered Warren Buffett Stock Analysis Agent.
This implementation wraps core functionality into a simple LangGraph workflow
so that every stock analysis request executes via a graph rather than a direct
LLM call. The graph has three asynchronous nodes:
1. gather_market_data  – Fetches all required market data.
2. llm_analysis        – Performs the heavy LLM reasoning using condensed knowledge.
3. compile_result      – Packages the final structured JSON response.

The public API mirrors the original WarrenBuffettAgent so that the FastAPI
router can drop-in replace the dependency with minimal code changes.
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END

from services.llm_service import LLMService
from services.knowledge_chunking_service import KnowledgeChunkingService
from tools.market_data_tool import MarketDataTool
from core.config import Config
from prompts.system_prompts import get_enhanced_warren_buffett_prompt

logger = logging.getLogger(__name__)


class AnalysisState(TypedDict):
    """State schema for the Warren Buffett analysis workflow."""
    symbol: str
    market_data: Dict[str, Any]
    analysis_result: Dict[str, Any]
    final_result: Dict[str, Any]
    error: Optional[str]


class LangGraphWarrenBuffettAgent:
    """LangGraph-based Warren Buffett analysis agent."""

    def __init__(self, config: Config):
        self.config = config
        self.llm_service = LLMService(config)
        self.market_tool = MarketDataTool(config)
        self.knowledge_service = KnowledgeChunkingService(config)
        self.knowledge_initialized = False
        self.condensed_knowledge = ""

        # Build the LangGraph workflow
        workflow = StateGraph(AnalysisState)
        workflow.add_node("gather_market_data", self._gather_market_data)
        workflow.add_node("llm_analysis", self._llm_analysis)
        workflow.add_node("compile_result", self._compile_result)

        # Wire the simple linear flow
        workflow.add_edge(START, "gather_market_data")
        workflow.add_edge("gather_market_data", "llm_analysis")
        workflow.add_edge("llm_analysis", "compile_result")
        workflow.add_edge("compile_result", END)
        
        self.graph = workflow.compile()

        logger.info("LangGraph Warren Buffett Agent initialized")

    # ------------------------------------------------------------------
    # Public interface (mirrors original agent)
    # ------------------------------------------------------------------
    async def analyze_stock(self, symbol: str) -> Dict[str, Any]:
        """Run the LangGraph workflow for a given stock symbol."""
        try:
            if not self.knowledge_initialized:
                await self._initialize_knowledge_base()

            initial_state = {
                "symbol": symbol,
                "market_data": {},
                "analysis_result": {},
                "final_result": {},
                "error": None
            }
            result: Dict[str, Any] = await self.graph.ainvoke(initial_state)
            return result.get("final_result", result)
        except Exception as e:
            logger.error(f"Graph execution error: {e}")
            return {
                "status": "error",
                "symbol": symbol,
                "error": str(e),
            }

    async def chat(self, message: str, thread_id: Optional[str] = None) -> Dict[str, Any]:
        """Fallback chat endpoint; uses simple LLM prompt + knowledge base."""
        try:
            if not self.knowledge_initialized:
                await self._initialize_knowledge_base()

            base_prompt = get_enhanced_warren_buffett_prompt()
            enhanced_system_prompt = (
                f"{base_prompt}\n\nENHANCED KNOWLEDGE BASE:\n{self.condensed_knowledge}\n"
            )

            messages = [
                {"role": "system", "content": enhanced_system_prompt},
                {"role": "user", "content": message},
            ]
            response = await self.llm_service.generate_response(messages, temperature=0.7)
            return {
                "status": "success",
                "response": response.get("content", "Unable to respond."),
                "thread_id": thread_id or f"chat_{hash(message) % 10000}",
                "knowledge_enhanced": True,
            }
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return {"status": "error", "error": str(e)}

    # ------------------------------------------------------------------
    # LangGraph NODE implementations
    # ------------------------------------------------------------------
    async def _gather_market_data(self, state: AnalysisState) -> Dict[str, Any]:
        """Gather market data for the given symbol."""
        symbol: str = state["symbol"]
        try:
            data = await self.market_tool.get_stock_data(symbol)
            if "error" in data:
                return {"error": data["error"]}
            return {"market_data": data}
        except Exception as e:
            logger.error(f"Market data gathering error: {e}")
            return {"error": str(e)}

    async def _llm_analysis(self, state: AnalysisState) -> Dict[str, Any]:
        """Perform LLM analysis using market data and knowledge base."""
        symbol = state["symbol"]
        market_data = state["market_data"]
        try:
            analysis = await self.llm_service.analyze_stock_with_knowledge(
                symbol, market_data, self.condensed_knowledge
            )
            if "error" in analysis:
                return {"error": analysis["error"]}
            return {"analysis_result": analysis}
        except Exception as e:
            logger.error(f"LLM analysis error: {e}")
            return {"error": str(e)}

    async def _compile_result(self, state: AnalysisState) -> Dict[str, Any]:
        """Compile the final analysis result."""
        symbol = state["symbol"]
        analysis = state["analysis_result"]
        market_data = state["market_data"]
        
        final_result = {
            "status": "success",
            "symbol": symbol,
            "analysis_type": "langgraph_warren_buffett",
            "result": {
                "analysis": analysis.get("analysis"),
                "score": analysis.get("score"),
                "recommendation": analysis.get("recommendation"),
                "summary": analysis.get("summary"),
                "reasoning": analysis.get("reasoning"),
                "risks": analysis.get("risks"),
                "criteria_scores": {
                    "profitability": analysis.get("profitability_score"),
                    "financial_strength": analysis.get("financial_strength_score"),
                    "valuation": analysis.get("valuation_score"),
                    "business_quality": analysis.get("business_quality_score"),
                    "growth": analysis.get("growth_score"),
                    "dividend_quality": analysis.get("dividend_quality_score"),
                },
                "market_data": market_data,
                "knowledge_enhanced": True,
            },
            "response": (
                f"LangGraph analysis complete for {symbol}. "
                f"Recommendation: {analysis.get('recommendation')} "
                f"with score {analysis.get('score')}/100."
            ),
            "thread_id": f"analysis_{symbol}_{hash(symbol) % 10000}",
        }
        
        return {"final_result": final_result}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    async def _initialize_knowledge_base(self) -> None:
        if self.knowledge_initialized:
            return
        logger.info("Processing knowledge base for LangGraph agent …")
        base_dir = Path(__file__).resolve().parent.parent
        cache_path = str(base_dir / "processed_knowledge.jsonl")
        if not self.knowledge_service.load_processed_knowledge(cache_path):
            await self.knowledge_service.initialize_knowledge_base()
            self.knowledge_service.save_processed_knowledge(cache_path)
        self.condensed_knowledge = self.knowledge_service.get_condensed_knowledge_for_prompt()
        self.knowledge_initialized = True
        logger.info("Knowledge base ready.")