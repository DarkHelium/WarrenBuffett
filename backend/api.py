"""
Main API for Warren Buffett Stock Analysis Agent
"""

import logging
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from core.config import Config
from agent.api import router as agent_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Warren Buffett Stock Analysis Agent",
    description="AI-powered stock analysis based on Warren Buffett's investment principles",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the agent router
app.include_router(agent_router)

# Global variables
config = None


@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    global config
    
    try:
        # Load configuration
        config = Config.from_env()
        config.validate()
        
        logger.info("Warren Buffett Stock Analysis Agent started successfully")
        
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    logger.info("Warren Buffett Stock Analysis Agent shutting down")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Warren Buffett Stock Analysis Agent",
        "version": "2.0.0",
        "description": "LangGraph-powered AI agent for stock analysis using Warren Buffett's investment principles",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "agent": "/agent/"
        },
        "available_features": [
            "Comprehensive stock analysis using Warren Buffett's criteria",
            "Real-time streaming analysis updates",
            "Conversational AI chat interface",
            "Integrated knowledge graph for historical insights",
            "Business quality and financial strength assessment",
            "Valuation analysis and investment recommendations"
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Check if config is loaded
        if not config:
            return {"status": "unhealthy", "reason": "Configuration not loaded"}
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "config": "loaded",
                "agent": "available"
            }
        }
        
    except Exception as e:
        return {"status": "unhealthy", "reason": str(e)}


@app.get("/config")
async def get_config():
    """Get current configuration (non-sensitive data only)."""
    try:
        if not config:
            raise HTTPException(status_code=503, detail="Configuration not loaded")
        
        return {
            "llm_provider": config.llm_provider,
            "max_conversation_history": config.max_conversation_history,
            "cache_duration_minutes": config.cache_duration_minutes,
            "max_stocks_per_request": config.max_stocks_per_request,
            "rate_limit_per_minute": config.rate_limit_per_minute,
            "server_host": config.server_host,
            "server_port": config.server_port
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting config: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    return app


if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )