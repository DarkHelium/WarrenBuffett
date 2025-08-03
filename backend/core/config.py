"""
Configuration module for Warren Buffett Stock Analysis Agent
"""

import logging
import os
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


@dataclass
class Config:
    """Configuration class for the Warren Buffett Agent."""
    
    # API Keys
    finnhub_api_key: str
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    alpha_vantage_api_key: Optional[str] = None
    alpaca_api_key: Optional[str] = None
    alpaca_api_secret: Optional[str] = None
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # Server properties for compatibility
    @property
    def server_host(self) -> str:
        return self.host
    
    @property
    def server_port(self) -> int:
        return self.port
    
    # Agent Configuration
    default_llm_provider: str = "openai"  # only openai supported now
    max_conversation_history: int = 50
    cache_duration_minutes: int = 15
    
    # LLM provider property for compatibility
    @property
    def llm_provider(self) -> str:
        return self.default_llm_provider
    
    # LLM model and API key properties for LangGraph integration
    @property
    def llm_model(self) -> str:
        """Get the appropriate model name based on the provider"""
        return "gpt-4.1-nano"

    @property
    def llm_api_key(self) -> str:
        """Get the appropriate API key based on the provider"""
        return self.openai_api_key
    
    # Market Data Configuration
    default_stock_limit: int = 50
    rate_limit_delay: float = 1.2
    max_retries: int = 3
    
    # Trading Configuration (if using Alpaca)
    alpaca_base_url: str = "https://paper-api.alpaca.markets/v2"
    trading_mode: str = "paper"  # paper, live
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Create configuration from environment variables."""
        return cls(
            # Required
            finnhub_api_key=os.getenv("FINNHUB_API_KEY", ""),
            
            # Optional API Keys
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    alpha_vantage_api_key=os.getenv("ALPHA_VANTAGE_API_KEY"),
    alpaca_api_key=os.getenv("ALPACA_API_KEY"),
    alpaca_api_secret=os.getenv("ALPACA_API_SECRET"),
            
            # Server
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", "8000")),
            debug=os.getenv("DEBUG", "false").lower() == "true",
            
            # Agent
            default_llm_provider=os.getenv("DEFAULT_LLM_PROVIDER", "openai"),
            max_conversation_history=int(os.getenv("MAX_CONVERSATION_HISTORY", "50")),
            cache_duration_minutes=int(os.getenv("CACHE_DURATION_MINUTES", "15")),
            
            # Market Data
            default_stock_limit=int(os.getenv("DEFAULT_STOCK_LIMIT", "50")),
            rate_limit_delay=float(os.getenv("RATE_LIMIT_DELAY", "1.2")),
            max_retries=int(os.getenv("MAX_RETRIES", "3")),
            
            # Trading
            alpaca_base_url=os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets/v2"),
            trading_mode=os.getenv("TRADING_MODE", "paper"),
        )
    
    def validate(self) -> bool:
        """Validate configuration."""
        if not self.finnhub_api_key:
            raise ValueError("FINNHUB_API_KEY is required")
        
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required")
        
        if self.default_llm_provider != "openai":
            logger.warning(f"Provider {self.default_llm_provider} is not supported. Defaulting to openai")
        
        return True