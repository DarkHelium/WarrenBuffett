"""
Warren Buffett Stock Analysis Agent with Knowledge Chunking
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from services.llm_service import LLMService
from services.knowledge_chunking_service import KnowledgeChunkingService
from tools.market_data_tool import MarketDataTool
from core.config import Config
from prompts.system_prompts import get_enhanced_warren_buffett_prompt

logger = logging.getLogger(__name__)


class WarrenBuffettAgent:
    """Warren Buffett investment analysis agent with knowledge chunking."""
    
    def __init__(self, config: Config):
        """Initialize the Warren Buffett agent."""
        self.config = config
        self.llm_service = LLMService(config)
        self.stock_tool = MarketDataTool(config)
        self.knowledge_service = KnowledgeChunkingService(config)
        self.knowledge_initialized = False
        self.condensed_knowledge = ""
        
        logger.info("Warren Buffett Agent initialized with knowledge chunking")
    
    async def initialize_knowledge_base(self) -> bool:
        """Initialize the knowledge base processing."""
        if self.knowledge_initialized:
            return True
        
        try:
            logger.info("Initializing Warren Buffett knowledge base...")
            
            # Try to load pre-processed knowledge first
            knowledge_cache_path = "processed_knowledge.json"
            if not self.knowledge_service.load_processed_knowledge(knowledge_cache_path):
                logger.info("No cached knowledge found, processing full knowledge base...")
                success = await self.knowledge_service.initialize_knowledge_base()
                if success:
                    # Save processed knowledge for future use
                    self.knowledge_service.save_processed_knowledge(knowledge_cache_path)
                    logger.info("Knowledge base processed and cached successfully")
                else:
                    logger.error("Failed to process knowledge base")
                    return False
            else:
                logger.info("Loaded cached processed knowledge")
            
            # Get condensed knowledge for prompts
            self.condensed_knowledge = self.knowledge_service.get_condensed_knowledge_for_prompt()
            self.knowledge_initialized = True
            
            logger.info(f"Knowledge base initialized. Condensed knowledge: {len(self.condensed_knowledge)} characters")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing knowledge base: {e}")
            return False
    
    async def analyze_stock(self, symbol: str) -> Dict[str, Any]:
        """
        Analyze a stock using Warren Buffett's investment principles.
        
        Args:
            symbol: Stock symbol to analyze
            
        Returns:
            Complete analysis results
        """
        try:
            logger.info(f"Starting analysis for {symbol}")
            
            # Ensure knowledge base is initialized
            if not self.knowledge_initialized:
                await self.initialize_knowledge_base()
            
            # Step 1: Gather market data
            market_data = await self._gather_market_data(symbol)
            if 'error' in market_data:
                return {
                    'status': 'error',
                    'symbol': symbol,
                    'error': market_data['error']
                }
            
            # Step 2: Perform LLM analysis with condensed knowledge
            analysis_result = await self.llm_service.analyze_stock_with_knowledge(
                symbol, 
                market_data, 
                self.condensed_knowledge
            )
            if 'error' in analysis_result:
                return {
                    'status': 'error',
                    'symbol': symbol,
                    'error': analysis_result['error']
                }
            
            # Step 3: Format final response
            final_result = {
                'status': 'success',
                'symbol': symbol,
                'analysis_type': 'warren_buffett_enhanced',
                'result': {
                    'analysis': analysis_result['analysis'],
                    'score': analysis_result['score'],
                    'recommendation': analysis_result['recommendation'],
                    'summary': analysis_result['summary'],
                    'reasoning': analysis_result['reasoning'],
                    'risks': analysis_result['risks'],
                    'criteria_scores': {
                        'profitability': analysis_result['profitability_score'],
                        'financial_strength': analysis_result['financial_strength_score'],
                        'valuation': analysis_result['valuation_score'],
                        'business_quality': analysis_result['business_quality_score'],
                        'growth': analysis_result['growth_score'],
                        'dividend_quality': analysis_result['dividend_quality_score']
                    },
                    'market_data': market_data,
                    'knowledge_enhanced': True
                },
                'response': f"Enhanced analysis complete for {symbol}. Recommendation: {analysis_result['recommendation']} with score {analysis_result['score']}/100.",
                'thread_id': f"analysis_{symbol}_{hash(symbol) % 10000}"
            }
            
            logger.info(f"Enhanced analysis completed for {symbol}: {analysis_result['recommendation']}")
            return final_result
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {str(e)}")
            return {
                'status': 'error',
                'symbol': symbol,
                'error': str(e)
            }
    
    async def _gather_market_data(self, symbol: str) -> Dict[str, Any]:
        """Gather market data for the stock."""
        try:
            # Get basic stock info (using get_stock_data which includes quote and profile)
            stock_data = await self.stock_tool.get_stock_data(symbol)
            if 'error' in stock_data:
                return stock_data
            
            # Get financial data (using get_fundamentals)
            financials = await self.stock_tool.get_fundamentals(symbol)
            
            # Combine all data
            market_data = {
                'basic_info': stock_data,
                'financials': financials if 'error' not in financials else {},
                'timestamp': self._get_current_timestamp()
            }
            
            return market_data
            
        except Exception as e:
            logger.error(f"Error gathering market data for {symbol}: {str(e)}")
            return {'error': str(e)}
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    async def chat(self, message: str, thread_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Handle chat messages and route to analysis if needed.
        
        Args:
            message: User message
            thread_id: Optional thread ID
            
        Returns:
            Chat response
        """
        try:
            # Ensure knowledge base is initialized
            if not self.knowledge_initialized:
                await self.initialize_knowledge_base()
            
            # Check if this is a stock analysis request
            if self._is_stock_analysis_request(message):
                symbol = self._extract_stock_symbol(message)
                if symbol:
                    return await self.analyze_stock(symbol)
            
            # Handle general chat using enhanced Warren Buffett prompt with condensed knowledge
            base_prompt = get_enhanced_warren_buffett_prompt()
            
            # Create enhanced system prompt with condensed knowledge
            enhanced_system_prompt = f"""
{base_prompt}

ENHANCED KNOWLEDGE BASE:
{self.condensed_knowledge}

Remember to draw from this comprehensive knowledge base when providing investment advice and analysis.
"""
            
            messages = [
                {"role": "system", "content": enhanced_system_prompt},
                {"role": "user", "content": message}
            ]
            
            response = await self.llm_service.generate_response(messages, temperature=0.7)
            
            return {
                'status': 'success',
                'response': response.get('content', 'I apologize, but I cannot provide a response at this time.'),
                'thread_id': thread_id or f"chat_{hash(message) % 10000}",
                'knowledge_enhanced': True
            }
            
        except Exception as e:
            logger.error(f"Error in chat: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _is_stock_analysis_request(self, message: str) -> bool:
        """Check if message is requesting stock analysis."""
        keywords = ['analyze', 'analysis', 'stock', 'investment', 'buy', 'sell', 'evaluate']
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in keywords)
    
    def _extract_stock_symbol(self, message: str) -> Optional[str]:
        """Extract stock symbol from message."""
        import re
        
        # Look for patterns like "AAPL", "analyze MSFT", etc.
        patterns = [
            r'\b([A-Z]{1,5})\b',  # 1-5 uppercase letters
            r'ticker[:\s]+([A-Z]{1,5})',
            r'symbol[:\s]+([A-Z]{1,5})',
            r'stock[:\s]+([A-Z]{1,5})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message.upper())
            if match:
                symbol = match.group(1)
                # Basic validation - common stock symbols
                if 1 <= len(symbol) <= 5 and symbol.isalpha():
                    return symbol
        
        return None