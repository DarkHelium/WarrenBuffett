"""
Search Tool for Warren Buffett Stock Analysis Agent
"""

import logging
from typing import Dict, List, Any, Optional
import re

from core.config import Config

logger = logging.getLogger(__name__)


class SearchTool:
    """
    Tool for searching and filtering stocks based on Warren Buffett's criteria.
    
    This tool provides various search and screening functions including:
    - Stock symbol search
    - Fundamental screening
    - Industry filtering
    - Quality scoring
    """
    
    def __init__(self, config: Config, market_data_tool):
        """Initialize the search tool."""
        self.config = config
        self.market_data_tool = market_data_tool
        logger.info("Search Tool initialized")
    
    async def search_stocks(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """
        Search for stocks by symbol or company name.
        
        Args:
            query: Search query (symbol or company name)
            limit: Maximum number of results
            
        Returns:
            Search results with stock information
        """
        try:
            # Get all available symbols
            symbols_data = await self.market_data_tool.get_stock_symbols()
            
            if 'error' in symbols_data:
                return symbols_data
            
            symbols = symbols_data.get('symbols', [])
            
            # Filter symbols based on query
            matches = []
            query_lower = query.lower()
            
            for symbol_info in symbols:
                symbol = symbol_info.get('symbol', '').lower()
                description = symbol_info.get('description', '').lower()
                
                # Check if query matches symbol or description
                if (query_lower in symbol or 
                    query_lower in description or
                    symbol.startswith(query_lower)):
                    matches.append(symbol_info)
                
                if len(matches) >= limit:
                    break
            
            return {
                'query': query,
                'matches': matches[:limit],
                'total_found': len(matches)
            }
            
        except Exception as e:
            logger.error(f"Error searching stocks: {str(e)}")
            return {'error': str(e)}
    
    async def screen_quality_stocks(self, criteria: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Screen stocks based on Warren Buffett's quality criteria.
        
        Args:
            criteria: Screening criteria (optional)
            
        Returns:
            List of quality stocks meeting criteria
        """
        try:
            # Default Warren Buffett criteria
            default_criteria = {
                'min_roe': 15,          # Minimum ROE
                'max_debt_equity': 0.5,  # Maximum debt-to-equity ratio
                'min_profit_margin': 10, # Minimum profit margin
                'min_market_cap': 1000,  # Minimum market cap (millions)
                'max_pe_ratio': 25,      # Maximum P/E ratio
                'min_current_ratio': 1.5 # Minimum current ratio
            }
            
            # Merge with provided criteria
            if criteria:
                default_criteria.update(criteria)
            
            # Get popular stocks to screen
            popular_stocks = await self.market_data_tool.get_popular_stocks()
            
            if 'error' in popular_stocks:
                return popular_stocks
            
            stocks = popular_stocks.get('stocks', [])
            quality_stocks = []
            
            for stock in stocks:
                symbol = stock.get('symbol')
                if not symbol:
                    continue
                
                # Get fundamental data for screening
                fundamentals = await self.market_data_tool.get_fundamentals(symbol)
                
                if 'error' in fundamentals:
                    continue
                
                # Apply screening criteria
                if self._meets_quality_criteria(fundamentals, default_criteria):
                    # Add screening score
                    score = self._calculate_quality_score(fundamentals)
                    stock['quality_score'] = score
                    stock['fundamentals_summary'] = self._extract_key_metrics(fundamentals)
                    quality_stocks.append(stock)
            
            # Sort by quality score (highest first)
            quality_stocks.sort(key=lambda x: x.get('quality_score', 0), reverse=True)
            
            return {
                'criteria_used': default_criteria,
                'total_screened': len(stocks),
                'quality_stocks': quality_stocks,
                'count': len(quality_stocks)
            }
            
        except Exception as e:
            logger.error(f"Error screening quality stocks: {str(e)}")
            return {'error': str(e)}
    
    async def find_undervalued_stocks(self, max_pe: float = 20, min_margin_safety: float = 15) -> Dict[str, Any]:
        """
        Find potentially undervalued stocks.
        
        Args:
            max_pe: Maximum P/E ratio
            min_margin_safety: Minimum margin of safety percentage
            
        Returns:
            List of potentially undervalued stocks
        """
        try:
            # Get popular stocks
            popular_stocks = await self.market_data_tool.get_popular_stocks()
            
            if 'error' in popular_stocks:
                return popular_stocks
            
            stocks = popular_stocks.get('stocks', [])
            undervalued_stocks = []
            
            for stock in stocks:
                symbol = stock.get('symbol')
                if not symbol:
                    continue
                
                # Get current quote and fundamentals
                quote_data = await self.market_data_tool.get_quote(symbol)
                fundamentals = await self.market_data_tool.get_fundamentals(symbol)
                
                if 'error' in quote_data or 'error' in fundamentals:
                    continue
                
                # Check valuation criteria
                if self._is_undervalued(quote_data, fundamentals, max_pe, min_margin_safety):
                    valuation_metrics = self._extract_valuation_metrics(quote_data, fundamentals)
                    stock['valuation_metrics'] = valuation_metrics
                    undervalued_stocks.append(stock)
            
            # Sort by margin of safety (highest first)
            undervalued_stocks.sort(
                key=lambda x: x.get('valuation_metrics', {}).get('margin_of_safety', 0), 
                reverse=True
            )
            
            return {
                'criteria': {
                    'max_pe_ratio': max_pe,
                    'min_margin_of_safety': min_margin_safety
                },
                'undervalued_stocks': undervalued_stocks,
                'count': len(undervalued_stocks)
            }
            
        except Exception as e:
            logger.error(f"Error finding undervalued stocks: {str(e)}")
            return {'error': str(e)}
    
    async def search_by_industry(self, industry: str, limit: int = 20) -> Dict[str, Any]:
        """
        Search stocks by industry sector.
        
        Args:
            industry: Industry name or keyword
            limit: Maximum number of results
            
        Returns:
            Stocks in the specified industry
        """
        try:
            # Get all symbols
            symbols_data = await self.market_data_tool.get_stock_symbols()
            
            if 'error' in symbols_data:
                return symbols_data
            
            symbols = symbols_data.get('symbols', [])
            industry_stocks = []
            industry_lower = industry.lower()
            
            # Filter by industry (this is a simplified approach)
            # In practice, you'd want to get company profiles for accurate industry classification
            for symbol_info in symbols:
                description = symbol_info.get('description', '').lower()
                
                # Check if industry keyword is in description
                if industry_lower in description:
                    industry_stocks.append(symbol_info)
                
                if len(industry_stocks) >= limit:
                    break
            
            return {
                'industry': industry,
                'stocks': industry_stocks[:limit],
                'count': len(industry_stocks)
            }
            
        except Exception as e:
            logger.error(f"Error searching by industry: {str(e)}")
            return {'error': str(e)}
    
    async def get_dividend_stocks(self, min_yield: float = 2.0) -> Dict[str, Any]:
        """
        Find stocks with attractive dividend yields.
        
        Args:
            min_yield: Minimum dividend yield percentage
            
        Returns:
            Dividend-paying stocks
        """
        try:
            # Get popular stocks
            popular_stocks = await self.market_data_tool.get_popular_stocks()
            
            if 'error' in popular_stocks:
                return popular_stocks
            
            stocks = popular_stocks.get('stocks', [])
            dividend_stocks = []
            
            for stock in stocks:
                symbol = stock.get('symbol')
                if not symbol:
                    continue
                
                # Get fundamental data
                fundamentals = await self.market_data_tool.get_fundamentals(symbol)
                
                if 'error' in fundamentals:
                    continue
                
                # Check dividend yield
                metrics = fundamentals.get('fundamentals', {})
                dividend_yield = metrics.get('dividend_yield', 0)
                
                if dividend_yield >= min_yield:
                    stock['dividend_yield'] = dividend_yield
                    stock['dividend_metrics'] = self._extract_dividend_metrics(fundamentals)
                    dividend_stocks.append(stock)
            
            # Sort by dividend yield (highest first)
            dividend_stocks.sort(key=lambda x: x.get('dividend_yield', 0), reverse=True)
            
            return {
                'min_yield_criteria': min_yield,
                'dividend_stocks': dividend_stocks,
                'count': len(dividend_stocks)
            }
            
        except Exception as e:
            logger.error(f"Error finding dividend stocks: {str(e)}")
            return {'error': str(e)}
    
    def _meets_quality_criteria(self, fundamentals: Dict, criteria: Dict) -> bool:
        """Check if stock meets quality criteria."""
        try:
            metrics = fundamentals.get('fundamentals', {})
            
            # Check each criterion
            roe = metrics.get('roe', 0)
            if roe < criteria.get('min_roe', 0):
                return False
            
            debt_equity = metrics.get('debt_to_equity', float('inf'))
            if debt_equity > criteria.get('max_debt_equity', float('inf')):
                return False
            
            profit_margin = metrics.get('net_margin', 0)
            if profit_margin < criteria.get('min_profit_margin', 0):
                return False
            
            pe_ratio = metrics.get('pe_ratio', float('inf'))
            if pe_ratio > criteria.get('max_pe_ratio', float('inf')):
                return False
            
            current_ratio = metrics.get('current_ratio', 0)
            if current_ratio < criteria.get('min_current_ratio', 0):
                return False
            
            return True
            
        except Exception:
            return False
    
    def _calculate_quality_score(self, fundamentals: Dict) -> float:
        """Calculate quality score (0-100)."""
        try:
            metrics = fundamentals.get('fundamentals', {})
            
            # ROE score (0-25 points)
            roe = metrics.get('roe', 0)
            roe_score = min(25, max(0, roe))
            
            # Profit margin score (0-25 points)
            margin = metrics.get('net_margin', 0)
            margin_score = min(25, max(0, margin))
            
            # Debt score (0-25 points, lower debt is better)
            debt_equity = metrics.get('debt_to_equity', 1)
            debt_score = max(0, 25 - (debt_equity * 25))
            
            # Growth score (0-25 points)
            revenue_growth = metrics.get('revenue_growth_3y', 0)
            growth_score = min(25, max(0, revenue_growth))
            
            total_score = roe_score + margin_score + debt_score + growth_score
            return round(total_score, 2)
            
        except Exception:
            return 0
    
    def _extract_key_metrics(self, fundamentals: Dict) -> Dict[str, Any]:
        """Extract key metrics for display."""
        try:
            metrics = fundamentals.get('fundamentals', {})
            
            return {
                'roe': metrics.get('roe', 0),
                'net_margin': metrics.get('net_margin', 0),
                'debt_to_equity': metrics.get('debt_to_equity', 0),
                'pe_ratio': metrics.get('pe_ratio', 0),
                'current_ratio': metrics.get('current_ratio', 0),
                'revenue_growth_3y': metrics.get('revenue_growth_3y', 0)
            }
            
        except Exception:
            return {}
    
    def _is_undervalued(self, quote_data: Dict, fundamentals: Dict, 
                       max_pe: float, min_margin_safety: float) -> bool:
        """Check if stock is undervalued."""
        try:
            metrics = fundamentals.get('fundamentals', {})
            quote = quote_data.get('quote', {})
            
            # Check P/E ratio
            pe_ratio = metrics.get('pe_ratio', float('inf'))
            if pe_ratio > max_pe:
                return False
            
            # Calculate simple margin of safety
            current_price = quote.get('current_price', 0)
            roe = metrics.get('roe', 0)
            
            if current_price > 0 and roe > 0:
                # Simplified intrinsic value calculation
                fair_pe = min(roe, 20)  # Cap at 20
                eps = current_price / pe_ratio if pe_ratio > 0 else 0
                intrinsic_value = eps * fair_pe
                
                if intrinsic_value > 0:
                    margin_of_safety = ((intrinsic_value - current_price) / intrinsic_value) * 100
                    return margin_of_safety >= min_margin_safety
            
            return False
            
        except Exception:
            return False
    
    def _extract_valuation_metrics(self, quote_data: Dict, fundamentals: Dict) -> Dict[str, Any]:
        """Extract valuation metrics."""
        try:
            metrics = fundamentals.get('fundamentals', {})
            quote = quote_data.get('quote', {})
            
            current_price = quote.get('current_price', 0)
            pe_ratio = metrics.get('pe_ratio', 0)
            roe = metrics.get('roe', 0)
            
            # Calculate margin of safety
            margin_of_safety = 0
            if current_price > 0 and roe > 0 and pe_ratio > 0:
                fair_pe = min(roe, 20)
                eps = current_price / pe_ratio
                intrinsic_value = eps * fair_pe
                
                if intrinsic_value > 0:
                    margin_of_safety = ((intrinsic_value - current_price) / intrinsic_value) * 100
            
            return {
                'current_price': current_price,
                'pe_ratio': pe_ratio,
                'pb_ratio': metrics.get('pb_ratio', 0),
                'margin_of_safety': round(margin_of_safety, 2),
                'estimated_fair_value': current_price * (1 + margin_of_safety / 100) if margin_of_safety > 0 else current_price
            }
            
        except Exception:
            return {}
    
    def _extract_dividend_metrics(self, fundamentals: Dict) -> Dict[str, Any]:
        """Extract dividend-related metrics."""
        try:
            metrics = fundamentals.get('fundamentals', {})
            
            return {
                'dividend_yield': metrics.get('dividend_yield', 0),
                'payout_ratio': metrics.get('payout_ratio', 0),
                'dividend_growth_3y': metrics.get('dividend_growth_3y', 0)
            }
            
        except Exception:
            return {}
    
    def validate_symbol(self, symbol: str) -> bool:
        """Validate if symbol format is correct."""
        # Basic symbol validation (letters, numbers, dots, hyphens)
        pattern = r'^[A-Z0-9.-]+$'
        return bool(re.match(pattern, symbol.upper())) and len(symbol) <= 10
    
    def format_search_results(self, results: List[Dict]) -> str:
        """Format search results for display."""
        if not results:
            return "No results found."
        
        formatted = []
        for i, result in enumerate(results[:10], 1):  # Limit to top 10
            symbol = result.get('symbol', 'N/A')
            description = result.get('description', 'N/A')
            formatted.append(f"{i}. {symbol} - {description}")
        
        return "\n".join(formatted)