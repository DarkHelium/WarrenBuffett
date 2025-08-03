"""
Simple LLM Service for Warren Buffett Stock Analysis Agent
"""

import logging
from typing import Dict, List, Any, Optional
import openai
from core.config import Config
from prompts.system_prompts import get_enhanced_warren_buffett_prompt

logger = logging.getLogger(__name__)


class LLMService:
    """Simple service for interacting with OpenAI GPT models."""
    
    def __init__(self, config: Config):
        """Initialize the LLM service."""
        self.config = config
        self.client = openai.AsyncOpenAI(api_key=config.openai_api_key)
        self.model_name = config.llm_model
        
        logger.info(f"LLM Service initialized with model: {self.model_name}")
    
    async def generate_response(self, messages: List[Dict[str, str]], 
                              temperature: float = 0.7, 
                              max_tokens: int = 1000) -> Dict[str, Any]:
        """
        Generate a response using OpenAI GPT.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens in response
            
        Returns:
            Response dictionary with content and metadata
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return {
                'content': response.choices[0].message.content,
                'model': response.model,
                'usage': {
                    'input_tokens': response.usage.prompt_tokens,
                    'output_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating LLM response: {str(e)}")
            return {'error': str(e)}
    
    async def analyze_stock_with_knowledge(self, symbol: str, market_data: Dict[str, Any], 
                                         condensed_knowledge: str) -> Dict[str, Any]:
        """
        Analyze a stock using Warren Buffett's investment principles with enhanced knowledge.
        
        Args:
            symbol: Stock symbol
            market_data: Market data for the stock
            condensed_knowledge: Condensed Warren Buffett knowledge base
            
        Returns:
            Analysis results
        """
        try:
            # Create enhanced system prompt with condensed knowledge
            base_prompt = get_enhanced_warren_buffett_prompt()
            
            enhanced_system_prompt = f"""
{base_prompt}

ENHANCED WARREN BUFFETT KNOWLEDGE BASE:
{condensed_knowledge}

Use this comprehensive knowledge base to provide the most accurate and insightful analysis possible, 
drawing from Warren Buffett's actual words, principles, and investment strategies.
"""

            user_prompt = f"""Analyze {symbol} based on the following data using Warren Buffett's proven investment principles:

Market Data: {market_data}

Please provide a comprehensive analysis including:
1. Overall investment score (0-100)
2. Investment recommendation (Strong Buy/Buy/Hold/Sell/Strong Sell)
3. Brief summary of key strengths and weaknesses
4. Specific reasoning for your recommendation based on Buffett's principles
5. Key risk factors
6. Individual scores for:
   - Profitability (0-100)
   - Financial Strength (0-100)
   - Valuation (0-100)
   - Business Quality (0-100)
   - Growth Prospects (0-100)
   - Dividend Quality (0-100)

Draw from Warren Buffett's actual investment wisdom and quote relevant principles where applicable.
Format your response clearly with these sections."""

            messages = [
                {"role": "system", "content": enhanced_system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response = await self.generate_response(messages, temperature=0.3, max_tokens=2000)
            
            if 'error' in response:
                return response
            
            # Parse the response to extract structured data
            analysis_text = response['content']
            
            # Extract scores using simple parsing
            scores = self._extract_scores(analysis_text)
            recommendation = self._extract_recommendation(analysis_text)
            
            return {
                'symbol': symbol,
                'analysis': analysis_text,
                'score': scores.get('overall', 75),
                'recommendation': recommendation,
                'summary': self._extract_summary(analysis_text),
                'reasoning': self._extract_reasoning(analysis_text),
                'risks': self._extract_risks(analysis_text),
                'profitability_score': scores.get('profitability', 75),
                'financial_strength_score': scores.get('financial_strength', 75),
                'valuation_score': scores.get('valuation', 75),
                'business_quality_score': scores.get('business_quality', 75),
                'growth_score': scores.get('growth', 75),
                'dividend_quality_score': scores.get('dividend_quality', 75),
                'knowledge_enhanced': True,
                'model_info': {
                    'model': response.get('model'),
                    'usage': response.get('usage')
                }
            }
            
        except Exception as e:
            logger.error(f"Error in enhanced stock analysis: {str(e)}")
            return {'error': str(e)}

    async def analyze_stock(self, symbol: str, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a stock using Warren Buffett's investment principles.
        
        Args:
            symbol: Stock symbol
            market_data: Market data for the stock
            
        Returns:
            Analysis results
        """
        try:
            # Use the enhanced Warren Buffett system prompt with complete knowledge base
            system_prompt = get_enhanced_warren_buffett_prompt()

            user_prompt = f"""Analyze {symbol} based on the following data:

Market Data: {market_data}

Please provide:
1. Overall investment score (0-100)
2. Investment recommendation (Strong Buy/Buy/Hold/Sell/Strong Sell)
3. Brief summary of key strengths and weaknesses
4. Specific reasoning for your recommendation
5. Key risk factors
6. Individual scores for:
   - Profitability (0-100)
   - Financial Strength (0-100)
   - Valuation (0-100)
   - Business Quality (0-100)
   - Growth Prospects (0-100)
   - Dividend Quality (0-100)

Format your response clearly with these sections."""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response = await self.generate_response(messages, temperature=0.3, max_tokens=1500)
            
            if 'error' in response:
                return response
            
            # Parse the response to extract structured data
            analysis_text = response['content']
            
            # Extract scores using simple parsing (you could make this more sophisticated)
            scores = self._extract_scores(analysis_text)
            recommendation = self._extract_recommendation(analysis_text)
            
            return {
                'symbol': symbol,
                'analysis': analysis_text,
                'score': scores.get('overall', 75),
                'recommendation': recommendation,
                'summary': self._extract_summary(analysis_text),
                'reasoning': self._extract_reasoning(analysis_text),
                'risks': self._extract_risks(analysis_text),
                'profitability_score': scores.get('profitability', 75),
                'financial_strength_score': scores.get('financial_strength', 75),
                'valuation_score': scores.get('valuation', 75),
                'business_quality_score': scores.get('business_quality', 75),
                'growth_score': scores.get('growth', 75),
                'dividend_quality_score': scores.get('dividend_quality', 75),
                'model_info': {
                    'model': response.get('model'),
                    'usage': response.get('usage')
                }
            }
            
        except Exception as e:
            logger.error(f"Error in stock analysis: {str(e)}")
            return {'error': str(e)}
    
    def _extract_scores(self, text: str) -> Dict[str, int]:
        """Extract numerical scores from analysis text."""
        scores = {}
        
        # Simple regex patterns to find scores
        import re
        
        # Look for patterns like "Overall score: 85" or "Profitability: 90/100"
        patterns = {
            'overall': r'overall.*?score.*?(\d+)',
            'profitability': r'profitability.*?(\d+)',
            'financial_strength': r'financial.*?strength.*?(\d+)',
            'valuation': r'valuation.*?(\d+)',
            'business_quality': r'business.*?quality.*?(\d+)',
            'growth': r'growth.*?(\d+)',
            'dividend_quality': r'dividend.*?quality.*?(\d+)'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, text.lower())
            if match:
                scores[key] = int(match.group(1))
            else:
                scores[key] = 75  # Default score
        
        return scores
    
    def _extract_recommendation(self, text: str) -> str:
        """Extract investment recommendation from analysis text."""
        text_lower = text.lower()
        
        if 'strong buy' in text_lower:
            return 'Strong Buy'
        elif 'buy' in text_lower:
            return 'Buy'
        elif 'sell' in text_lower:
            return 'Sell'
        elif 'strong sell' in text_lower:
            return 'Strong Sell'
        else:
            return 'Hold'
    
    def _extract_summary(self, text: str) -> str:
        """Extract summary from analysis text."""
        lines = text.split('\n')
        for line in lines:
            if 'summary' in line.lower() and len(line) > 20:
                return line.strip()
        
        # Return first substantial line if no summary found
        for line in lines:
            if len(line.strip()) > 50:
                return line.strip()
        
        return "Analysis completed successfully."
    
    def _extract_reasoning(self, text: str) -> List[str]:
        """Extract reasoning points from analysis text."""
        lines = text.split('\n')
        reasoning = []
        
        for line in lines:
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
                reasoning.append(line)
        
        if not reasoning:
            # Extract sentences that contain key reasoning words
            sentences = text.split('.')
            for sentence in sentences:
                if any(word in sentence.lower() for word in ['because', 'due to', 'strong', 'weak', 'advantage']):
                    reasoning.append(sentence.strip())
        
        return reasoning[:5]  # Limit to 5 points
    
    def _extract_risks(self, text: str) -> List[str]:
        """Extract risk factors from analysis text."""
        lines = text.split('\n')
        risks = []
        
        in_risk_section = False
        for line in lines:
            line = line.strip()
            if 'risk' in line.lower():
                in_risk_section = True
                if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                    risks.append(line)
            elif in_risk_section and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
                risks.append(line)
            elif in_risk_section and line and not line.startswith('-') and not line.startswith('•') and not line.startswith('*'):
                in_risk_section = False
        
        if not risks:
            risks = ["Market volatility", "Economic uncertainty", "Industry-specific risks"]
        
        return risks[:5]  # Limit to 5 risks