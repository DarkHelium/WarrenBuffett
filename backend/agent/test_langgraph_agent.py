"""
Test script for LangGraph Warren Buffett Agent

This script tests the core functionality of the LangGraph-based agent including:
- Stock analysis workflow
- Chat functionality
- Streaming capabilities
- Memory and conversation management
"""

import asyncio
import logging
import pytest

# Mark entire module for asynchronous pytest
pytestmark = pytest.mark.asyncio
import json
from datetime import datetime
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import Config
from agent.langgraph_warren_buffett_agent import LangGraphWarrenBuffettAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_stock_analysis():
    """Test the stock analysis workflow"""
    print("\n" + "="*60)
    print("🧪 TESTING STOCK ANALYSIS WORKFLOW")
    print("="*60)
    
    try:
        # Initialize config (you may need to adjust this based on your config setup)
        config = Config()
        
        # Initialize the LangGraph agent
        agent = LangGraphWarrenBuffettAgent(config)
        
        # Test stock analysis
        test_symbol = "AAPL"
        print(f"\n📊 Analyzing {test_symbol} using LangGraph workflow...")
        
        result = await agent.analyze_stock(
            symbol=test_symbol,
            analysis_type="comprehensive"
        )
        
        print(f"\n✅ Analysis Result:")
        print(f"Status: {result['status']}")
        print(f"Symbol: {result.get('symbol', 'N/A')}")
        print(f"Thread ID: {result.get('thread_id', 'N/A')}")
        
        if result['status'] == 'success':
            final_state = result['result']
            print(f"\n📈 Analysis Scores:")
            print(f"Business Quality: {final_state.get('business_quality_score', 'N/A')}/100")
            print(f"Financial Strength: {final_state.get('financial_strength_score', 'N/A')}/100")
            print(f"Valuation: {final_state.get('valuation_score', 'N/A')}/100")
            print(f"Recommendation: {final_state.get('investment_recommendation', 'N/A')}")
            print(f"Confidence: {final_state.get('confidence_level', 'N/A')}%")
            
            risk_factors = final_state.get('risk_factors', [])
            if risk_factors:
                print(f"\n⚠️ Risk Factors:")
                for risk in risk_factors:
                    print(f"  • {risk}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error in stock analysis test: {str(e)}")
        logger.error(f"Stock analysis test failed: {str(e)}")
        return None


async def test_chat_functionality():
    """Test the chat functionality"""
    print("\n" + "="*60)
    print("💬 TESTING CHAT FUNCTIONALITY")
    print("="*60)
    
    try:
        config = Config()
        agent = LangGraphWarrenBuffettAgent(config)
        
        # Test general investment chat
        chat_messages = [
            "What are Warren Buffett's key investment principles?",
            "How do you evaluate a company's moat?",
            "What should I look for in a company's financial statements?",
            "Analyze MSFT"  # This should trigger stock analysis
        ]
        
        thread_id = f"test_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        for i, message in enumerate(chat_messages, 1):
            print(f"\n💬 Chat Message {i}: {message}")
            
            result = await agent.chat(message=message, thread_id=thread_id)
            
            print(f"✅ Response Status: {result['status']}")
            if result['status'] == 'success':
                response = result['response']
                print(f"🤖 Agent Response: {response[:200]}...")
                if len(response) > 200:
                    print("    [Response truncated for display]")
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
        
        # Test conversation history
        print(f"\n📚 Testing conversation history...")
        history = agent.get_conversation_history(thread_id)
        print(f"✅ Retrieved {len(history)} messages from conversation history")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in chat functionality test: {str(e)}")
        logger.error(f"Chat functionality test failed: {str(e)}")
        return False


async def test_streaming_analysis():
    """Test streaming analysis functionality"""
    print("\n" + "="*60)
    print("🌊 TESTING STREAMING ANALYSIS")
    print("="*60)
    
    try:
        config = Config()
        agent = LangGraphWarrenBuffettAgent(config)
        
        # Create initial state for streaming
        symbol = "GOOGL"
        initial_state = {
            "messages": [],
            "current_symbol": symbol,
            "analysis_type": "comprehensive",
            "analysis_stage": "data_gathering",
            "requires_human_review": False
        }
        
        config_dict = {
            "configurable": {
                "thread_id": f"stream_test_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
        }
        
        print(f"🌊 Starting streaming analysis for {symbol}...")
        
        step_count = 0
        async for chunk in agent.graph.astream(initial_state, config=config_dict):
            step_count += 1
            for node_name, node_output in chunk.items():
                print(f"📡 Step {step_count} - Node: {node_name}")
                
                if "messages" in node_output and node_output["messages"]:
                    latest_message = node_output["messages"][-1]
                    print(f"   Message: {latest_message.content}")
                
                if "analysis_stage" in node_output:
                    print(f"   Stage: {node_output['analysis_stage']}")
                
                # Print scores if available
                for score_key in ["business_quality_score", "financial_strength_score", "valuation_score"]:
                    if score_key in node_output and node_output[score_key] is not None:
                        print(f"   {score_key.replace('_', ' ').title()}: {node_output[score_key]}")
        
        print(f"✅ Streaming analysis completed in {step_count} steps")
        return True
        
    except Exception as e:
        print(f"❌ Error in streaming analysis test: {str(e)}")
        logger.error(f"Streaming analysis test failed: {str(e)}")
        return False


async def test_knowledge_base_integration():
    """Test Warren Buffett knowledge base integration"""
    print("\n" + "="*60)
    print("📚 TESTING KNOWLEDGE BASE INTEGRATION")
    print("="*60)
    
    try:
        # Test the knowledge base functions
        from prompts.warren_buffett_knowledge_loader import (
            get_warren_buffett_knowledge,
            get_knowledge_stats,
            search_knowledge
        )
        
        print("📊 Getting knowledge base statistics...")
        stats = get_knowledge_stats()
        print(f"✅ Knowledge Base Stats:")
        print(f"   Total Files: {stats['total_files']}")
        print(f"   Books: {stats['books']}")
        print(f"   Transcripts: {stats['transcripts']}")
        print(f"   Total Characters: {stats['total_characters']:,}")
        print(f"   Total Words: {stats['total_words']:,}")
        
        print(f"\n🔍 Testing knowledge search...")
        search_terms = ["circle of competence", "margin of safety", "intrinsic value"]
        
        for term in search_terms:
            results = search_knowledge(term)
            print(f"   '{term}': {len(results)} matches found")
            if results:
                print(f"      Sample: {results[0]['content'][:100]}...")
        
        print(f"\n✅ Knowledge base integration working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Error in knowledge base integration test: {str(e)}")
        logger.error(f"Knowledge base integration test failed: {str(e)}")
        return False


async def run_all_tests():
    """Run all tests"""
    print("🚀 STARTING LANGGRAPH WARREN BUFFETT AGENT TESTS")
    print("="*80)
    
    test_results = {}
    
    # Test 1: Knowledge Base Integration
    test_results['knowledge_base'] = await test_knowledge_base_integration()
    
    # Test 2: Stock Analysis Workflow
    test_results['stock_analysis'] = await test_stock_analysis() is not None
    
    # Test 3: Chat Functionality
    test_results['chat_functionality'] = await test_chat_functionality()
    
    # Test 4: Streaming Analysis
    test_results['streaming_analysis'] = await test_streaming_analysis()
    
    # Summary
    print("\n" + "="*80)
    print("📋 TEST SUMMARY")
    print("="*80)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    for test_name, passed in test_results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\n🎯 Overall Result: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! LangGraph Warren Buffett Agent is ready to use.")
    else:
        print("⚠️ Some tests failed. Please check the error messages above.")
    
    return test_results


if __name__ == "__main__":
    # Run the tests
    asyncio.run(run_all_tests())