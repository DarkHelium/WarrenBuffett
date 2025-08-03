"""
Main entry point for Warren Buffett Stock Analysis Agent
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from core.config import Config
from api import create_app
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('warren_buffett_agent.log')
    ]
)

logger = logging.getLogger(__name__)

# Create the FastAPI app at module level for uvicorn
config = Config.from_env()
app = create_app()


def main():
    """Main function to start the Warren Buffett Stock Analysis Agent."""
    try:
        # Validate configuration
        try:
            config.validate()
            logger.info("Configuration validated successfully")
        except ValueError as e:
            logger.error(f"Configuration validation failed: {str(e)}")
            logger.info("Please check your .env file and ensure all required API keys are set")
            sys.exit(1)
        
        # Start the server
        logger.info(f"Starting Warren Buffett Stock Analysis Agent on {config.server_host}:{config.server_port}")
        logger.info(f"Using LLM provider: {config.llm_provider}")
        logger.info("API Documentation available at: http://localhost:8000/docs")
        
        uvicorn.run(
            app,
            host=config.server_host,
            port=config.server_port,
            log_level="info",
            access_log=True
        )
        
    except KeyboardInterrupt:
        logger.info("Shutting down Warren Buffett Stock Analysis Agent...")
    except Exception as e:
        logger.error(f"Failed to start Warren Buffett Stock Analysis Agent: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()