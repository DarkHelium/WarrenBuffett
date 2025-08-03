"""
Simple API Router for Warren Buffett Stock Analysis Agent
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from agent.warren_buffett_agent import WarrenBuffettAgent
from core.config import Config

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/agent", tags=["agent"])

# Initialize agent
config = Config.from_env()
agent = WarrenBuffettAgent(config)


class StockAnalysisRequest(BaseModel):
    """Request model for stock analysis."""
    symbol: str
    analysis_type: str = "warren_buffett"


class ChatRequest(BaseModel):
    """Request model for chat."""
    message: str
    thread_id: str = None


@router.post("/analyze")
async def analyze_stock(request: StockAnalysisRequest) -> JSONResponse:
    """
    Analyze a stock using Warren Buffett's investment principles.
    
    Args:
        request: Stock analysis request
        
    Returns:
        Analysis results
    """
    try:
        logger.info(f"Received analysis request for {request.symbol}")
        
        # Validate symbol
        if not request.symbol or len(request.symbol) > 10:
            raise HTTPException(status_code=400, detail="Invalid stock symbol")
        
        # Perform analysis
        result = await agent.analyze_stock(request.symbol.upper())
        
        # Log the response for debugging
        logger.info(f"Analysis result for {request.symbol}: {result.get('status')}")
        print(f"DEBUG - Analysis Response: {result}")
        
        # Return JSON response
        return JSONResponse(
            status_code=200,
            content=result,
            headers={"Content-Type": "application/json"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in analyze endpoint: {str(e)}")
        error_response = {
            'status': 'error',
            'symbol': request.symbol,
            'error': str(e)
        }
        return JSONResponse(
            status_code=500,
            content=error_response,
            headers={"Content-Type": "application/json"}
        )


@router.post("/chat")
async def chat(request: ChatRequest) -> JSONResponse:
    """
    Chat with Warren Buffett agent.
    
    Args:
        request: Chat request
        
    Returns:
        Chat response
    """
    try:
        logger.info(f"Received chat request: {request.message[:50]}...")
        
        # Validate message
        if not request.message or len(request.message) > 1000:
            raise HTTPException(status_code=400, detail="Invalid message")
        
        # Process chat
        result = await agent.chat(request.message, request.thread_id)
        
        # Log the response for debugging
        logger.info(f"Chat result: {result.get('status')}")
        print(f"DEBUG - Chat Response: {result}")
        
        # Return JSON response
        return JSONResponse(
            status_code=200,
            content=result,
            headers={"Content-Type": "application/json"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        error_response = {
            'status': 'error',
            'error': str(e)
        }
        return JSONResponse(
            status_code=500,
            content=error_response,
            headers={"Content-Type": "application/json"}
        )


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Warren Buffett Stock Analysis Agent",
        "version": "1.0.0"
    }