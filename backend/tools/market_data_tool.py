"""
Market Data Tool for Warren Buffett Stock Analysis Agent
"""

import finnhub
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from core.config import Config

logger = logging.getLogger(__name__)


@dataclass
class StockQuote:
    """Stock quote data structure."""
    symbol: str
    current_price: float
    change: float
    percent_change: float
    high_price: float
    low_price: float
    open_price: float
    previous_close: float
    timestamp: int


@dataclass
class StockInfo:
    """Stock information data structure."""
    symbol: str
    description: str
    display_symbol: str
    type: str
    currency: str = "USD"
    mic: Optional[str] = None


class MarketDataTool:
    """
    Tool for fetching market data using Finnhub API.
    
    Provides real-time quotes, stock information, and fundamental data
    following Warren Buffett's analysis requirements.
    """
    
    def __init__(self, config: Config):
        """Initialize the market data tool."""
        self.config = config
        self.client = finnhub.Client(api_key=config.finnhub_api_key)
        
        # Caching
        self.cache = {}
        self.cache_duration = timedelta(minutes=config.cache_duration_minutes)
        self.quote_cache_duration = timedelta(minutes=1)
        
        # Rate limiting
        self.last_api_call = {}
        self.min_call_interval = config.rate_limit_delay
        self.max_retries = config.max_retries
        
        logger.info("Market Data Tool initialized")
    
    def _is_cache_valid(self, key: str, duration: timedelta = None) -> bool:
        """Check if cached data is still valid."""
        if key not in self.cache:
            return False
        
        cached_time = self.cache[key].get('timestamp')
        if not cached_time:
            return False
        
        cache_duration = duration or self.cache_duration
        return datetime.now() - cached_time < cache_duration
    
    def _get_cached_data(self, key: str, duration: timedelta = None) -> Optional[Any]:
        """Get cached data if valid."""
        if self._is_cache_valid(key, duration):
            return self.cache[key]['data']
        return None
    
    def _set_cache(self, key: str, data: Any):
        """Set data in cache."""
        self.cache[key] = {
            'data': data,
            'timestamp': datetime.now()
        }
    
    async def _rate_limit_check(self, symbol: str = "general") -> bool:
        """Check if we can make an API call without hitting rate limits."""
        now = datetime.now()
        if symbol in self.last_api_call:
            time_since_last = (now - self.last_api_call[symbol]).total_seconds()
            if time_since_last < self.min_call_interval:
                await asyncio.sleep(self.min_call_interval - time_since_last)
        
        self.last_api_call[symbol] = now
        return True
    
    async def get_stock_data(self, symbol: str) -> Dict[str, Any]:
        """
        Get comprehensive stock data including quote and basic info.
        
        Args:
            symbol: Stock symbol to fetch data for
            
        Returns:
            Dictionary containing stock data
        """
        try:
            # Get quote data
            quote_data = await self.get_quote(symbol)
            if quote_data.get('status') != 'success':
                return quote_data
            
            # Get company profile
            profile_data = await self.get_company_profile(symbol)
            
            return {
                'status': 'success',
                'symbol': symbol,
                'quote': quote_data.get('quote', {}),
                'profile': profile_data.get('profile', {}),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting stock data for {symbol}: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    async def get_quote(self, symbol: str) -> Dict[str, Any]:
        """Get real-time quote for a stock."""
        cache_key = f"quote_{symbol}"
        cached_data = self._get_cached_data(cache_key, self.quote_cache_duration)
        
        if cached_data:
            return cached_data
        
        await self._rate_limit_check(symbol)
        
        for attempt in range(self.max_retries):
            try:
                quote_data = self.client.quote(symbol)
                
                if not quote_data or 'c' not in quote_data:
                    return {'status': 'error', 'error': f'No quote data found for {symbol}'}
                
                formatted_quote = {
                    'status': 'success',
                    'symbol': symbol.upper(),
                    'quote': {
                        'current_price': quote_data.get('c', 0),
                        'change': quote_data.get('d', 0),
                        'percent_change': quote_data.get('dp', 0),
                        'high_price': quote_data.get('h', 0),
                        'low_price': quote_data.get('l', 0),
                        'open_price': quote_data.get('o', 0),
                        'previous_close': quote_data.get('pc', 0),
                        'timestamp': quote_data.get('t', int(datetime.now().timestamp()))
                    },
                    'updated_at': datetime.now().isoformat()
                }
                
                self._set_cache(cache_key, formatted_quote)
                return formatted_quote
                
            except Exception as e:
                logger.warning(f"Error fetching quote for {symbol} (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                else:
                    return {'status': 'error', 'error': f'Failed to get quote for {symbol}: {str(e)}'}
    
    async def get_company_profile(self, symbol: str) -> Dict[str, Any]:
        """Get company profile information."""
        cache_key = f"profile_{symbol}"
        cached_data = self._get_cached_data(cache_key)
        
        if cached_data:
            return cached_data
        
        await self._rate_limit_check(f"profile_{symbol}")
        
        try:
            profile_data = self.client.company_profile2(symbol=symbol)
            
            if not profile_data:
                return {'status': 'error', 'error': f'No profile data found for {symbol}'}
            
            formatted_profile = {
                'status': 'success',
                'symbol': symbol.upper(),
                'profile': {
                    'name': profile_data.get('name', ''),
                    'country': profile_data.get('country', ''),
                    'currency': profile_data.get('currency', 'USD'),
                    'exchange': profile_data.get('exchange', ''),
                    'industry': profile_data.get('finnhubIndustry', ''),
                    'ipo': profile_data.get('ipo', ''),
                    'market_cap': profile_data.get('marketCapitalization', 0),
                    'shares_outstanding': profile_data.get('shareOutstanding', 0),
                    'website': profile_data.get('weburl', ''),
                    'logo': profile_data.get('logo', ''),
                    'phone': profile_data.get('phone', ''),
                    'description': profile_data.get('description', '')
                },
                'updated_at': datetime.now().isoformat()
            }
            
            self._set_cache(cache_key, formatted_profile)
            return formatted_profile
            
        except Exception as e:
            logger.error(f"Error getting company profile for {symbol}: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    async def get_fundamentals(self, symbol: str) -> Dict[str, Any]:
        """Get fundamental data for a stock."""
        cache_key = f"fundamentals_{symbol}"
        cached_data = self._get_cached_data(cache_key)
        
        if cached_data:
            return cached_data
        
        await self._rate_limit_check(f"fundamentals_{symbol}")
        
        try:
            # Get basic financials
            financials = self.client.company_basic_financials(symbol, 'all')
            
            if not financials:
                return {'status': 'error', 'error': f'No fundamental data found for {symbol}'}
            
            metrics = financials.get('metric', {})
            
            formatted_fundamentals = {
                'status': 'success',
                'symbol': symbol.upper(),
                'fundamentals': {
                    # Profitability metrics
                    'roe': metrics.get('roe', 0),  # Return on Equity
                    'roa': metrics.get('roa', 0),  # Return on Assets
                    'roic': metrics.get('roic', 0),  # Return on Invested Capital
                    'gross_margin': metrics.get('grossMargin', 0),
                    'operating_margin': metrics.get('operatingMargin', 0),
                    'net_margin': metrics.get('netProfitMargin', 0),
                    
                    # Valuation metrics
                    'pe_ratio': metrics.get('peBasicExclExtraTTM', 0),
                    'pb_ratio': metrics.get('pbQuarterly', 0),
                    'ps_ratio': metrics.get('psQuarterly', 0),
                    'peg_ratio': metrics.get('pegRatio', 0),
                    'ev_ebitda': metrics.get('evEbitdaTTM', 0),
                    
                    # Financial strength
                    'debt_to_equity': metrics.get('totalDebt/totalEquityQuarterly', 0),
                    'current_ratio': metrics.get('currentRatioQuarterly', 0),
                    'quick_ratio': metrics.get('quickRatioQuarterly', 0),
                    'cash_ratio': metrics.get('cashRatioQuarterly', 0),
                    
                    # Growth metrics
                    'revenue_growth_3y': metrics.get('revenueGrowth3Y', 0),
                    'revenue_growth_5y': metrics.get('revenueGrowth5Y', 0),
                    'eps_growth_3y': metrics.get('epsGrowth3Y', 0),
                    'eps_growth_5y': metrics.get('epsGrowth5Y', 0),
                    
                    # Dividend metrics
                    'dividend_yield': metrics.get('dividendYieldIndicatedAnnual', 0),
                    'payout_ratio': metrics.get('payoutRatioTTM', 0),
                    
                    # Other important metrics
                    'beta': metrics.get('beta', 0),
                    '52_week_high': metrics.get('52WeekHigh', 0),
                    '52_week_low': metrics.get('52WeekLow', 0),
                },
                'updated_at': datetime.now().isoformat()
            }
            
            self._set_cache(cache_key, formatted_fundamentals)
            return formatted_fundamentals
            
        except Exception as e:
            logger.error(f"Error getting fundamentals for {symbol}: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    async def get_financial_metrics(self, symbol: str) -> Dict[str, Any]:
        """Get financial metrics for a stock (alias for get_fundamentals for compatibility)."""
        # This method is an alias for get_fundamentals to maintain compatibility
        # with the LangGraph agent that expects this method name
        return await self.get_fundamentals(symbol)
    
    async def get_popular_stocks(self, limit: int = 10) -> Dict[str, Any]:
        """Get popular stocks with quotes."""
        try:
            # Popular US stocks (you can customize this list)
            popular_symbols = [
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA',
                'META', 'NVDA', 'BRK-B', 'JNJ', 'V',
                'WMT', 'PG', 'UNH', 'HD', 'MA',
                'DIS', 'PYPL', 'ADBE', 'NFLX', 'CRM'
            ]
            
            # Limit to requested number
            symbols_to_fetch = popular_symbols[:limit]
            
            # Get quotes for all symbols
            quotes = []
            for symbol in symbols_to_fetch:
                quote_data = await self.get_quote(symbol)
                if quote_data.get('status') == 'success':
                    quotes.append(quote_data)
                
                # Small delay between calls
                await asyncio.sleep(0.5)
            
            return {
                'status': 'success',
                'count': len(quotes),
                'stocks': quotes,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting popular stocks: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    async def search_stocks(self, query: str) -> Dict[str, Any]:
        """Search for stocks by symbol or company name."""
        cache_key = f"search_{query.lower()}"
        cached_data = self._get_cached_data(cache_key)
        
        if cached_data:
            return cached_data
        
        await self._rate_limit_check("search")
        
        try:
            # Get all US stocks (cached)
            stocks_data = self.client.stock_symbols('US')
            
            # Filter based on query
            query_lower = query.lower()
            matching_stocks = []
            
            for stock in stocks_data:
                if (query_lower in stock.get('symbol', '').lower() or 
                    query_lower in stock.get('description', '').lower()):
                    matching_stocks.append({
                        'symbol': stock.get('symbol', ''),
                        'description': stock.get('description', ''),
                        'display_symbol': stock.get('displaySymbol', ''),
                        'type': stock.get('type', ''),
                        'currency': stock.get('currency', 'USD')
                    })
                
                # Limit results
                if len(matching_stocks) >= 20:
                    break
            
            result = {
                'status': 'success',
                'query': query,
                'count': len(matching_stocks),
                'stocks': matching_stocks,
                'timestamp': datetime.now().isoformat()
            }
            
            self._set_cache(cache_key, result)
            return result
            
        except Exception as e:
            logger.error(f"Error searching stocks with query '{query}': {str(e)}")
            return {'status': 'error', 'error': str(e)}