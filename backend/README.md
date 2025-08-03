# Warren Buffett Stock Analysis System

An AI-powered stock analysis system that applies Warren Buffett's investment principles using LangGraph for agent orchestration and advanced reasoning.

## 🏗️ Architecture

The backend follows a modular architecture with LangGraph as the core agent framework:

```
backend/
├── agent/                  # LangGraph agent implementation
│   ├── __init__.py
│   └── langgraph_warren_buffett_agent.py
├── core/                   # Core configuration and utilities
│   ├── __init__.py
│   └── config.py
├── prompts/                # System prompts and templates
│   ├── __init__.py
│   └── system_prompts.py
├── services/               # External service integrations
│   ├── __init__.py
│   └── llm_service.py
├── tools/                  # Analysis and data tools
│   ├── __init__.py
│   ├── analysis_tool.py
│   ├── market_data_tool.py
│   └── search_tool.py
├── api.py                  # FastAPI application
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
└── .env.example           # Environment variables template
```

## 🚀 Features

### Core Analysis Capabilities
- **Fundamental Analysis**: Deep dive into company financials using Buffett's criteria
- **Business Quality Assessment**: Evaluate competitive moats and management quality
- **Valuation Analysis**: Intrinsic value calculation with margin of safety
- **Risk Assessment**: Comprehensive risk evaluation framework
- **Investment Recommendations**: Clear buy/hold/sell recommendations with reasoning

### LangGraph Agent Features
- **Multi-step Reasoning**: Chain-of-thought analysis process
- **State Management**: Persistent conversation state across interactions
- **Tool Integration**: Seamless integration with market data and analysis tools
- **Streaming Support**: Real-time analysis with streaming responses
- **Thread Management**: Conversation history and context tracking

### Search and Screening
- **Stock Search**: Find stocks by symbol or company name
- **Quality Screening**: Filter stocks based on Buffett's quality criteria
- **Undervalued Stock Discovery**: Identify potentially undervalued opportunities
- **Dividend Stock Analysis**: Find attractive dividend-paying stocks

### AI-Powered Chat
- **Investment Guidance**: Chat with an AI that thinks like Warren Buffett
- **Educational Content**: Learn about value investing principles
- **Market Analysis**: Get insights on market conditions and opportunities

## 🛠️ Setup

### 1. Environment Setup

Copy the environment template:
```bash
cp .env.example .env
```

Configure your API keys in `.env`:
```env
# Required: Market Data
FINNHUB_API_KEY=your_finnhub_api_key

# Required: AI Services (choose one)
OPENAI_API_KEY=your_openai_api_key
# OR
ANTHROPIC_API_KEY=your_anthropic_api_key

# Optional: Additional Data Sources
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
ALPACA_API_KEY=your_alpaca_key
ALPACA_SECRET_KEY=your_alpaca_secret

# Configuration
LLM_PROVIDER=openai  # or 'anthropic'
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Application

```bash
python main.py
```

The API will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📡 API Endpoints

### Stock Analysis
- `POST /analyze` - Comprehensive stock analysis
- `GET /popular` - Get popular stocks for analysis
- `POST /search` - Search stocks by symbol or name

### Screening & Filtering
- `POST /screen` - Screen quality stocks
- `GET /undervalued` - Find undervalued stocks
- `GET /dividends` - Find dividend stocks

### LangGraph Agent
- `POST /chat` - Chat with Warren Buffett agent
- `POST /analyze/stream` - Real-time streaming analysis
- `GET /conversation/{thread_id}` - Get conversation history

### System
- `GET /health` - Health check
- `GET /config` - Current configuration

## 🧠 Warren Buffett's Investment Principles

The agent implements these core principles:

### Business Quality
- **High ROE**: Consistent returns on equity (>15%)
- **Strong Margins**: Healthy profit margins
- **Low Debt**: Conservative debt levels
- **Predictable Earnings**: Consistent growth patterns

### Valuation
- **Margin of Safety**: Buy below intrinsic value
- **Reasonable P/E**: Avoid overvalued stocks
- **Long-term Value**: Focus on sustainable competitive advantages

### Investment Approach
- **Quality over Quantity**: Few, high-quality investments
- **Long-term Horizon**: Hold for years, not months
- **Understand the Business**: Invest in comprehensible companies
- **Management Quality**: Strong, shareholder-friendly leadership

## 🔧 Configuration

### LLM Providers
- **OpenAI**: GPT-4 for analysis and chat
- **Anthropic**: Claude-3 for analysis and chat

### Market Data Sources
- **Finnhub**: Primary real-time data source
- **Alpha Vantage**: Fundamental data backup
- **Alpaca**: Trading integration (optional)
- **Yahoo Finance**: Additional data source

### Caching & Performance
- **Memory Caching**: Fast repeated requests
- **Disk Caching**: Persistent data storage
- **Rate Limiting**: Respect API limits
- **Async Processing**: Non-blocking operations

## 📊 Example Usage

### Basic Stock Analysis
```python
import requests

# Analyze Apple stock
response = requests.post(
    "http://localhost:8000/analyze",
    json={"symbol": "AAPL"}
)
print(response.json())
```

### Chat with the Agent
```python
# Start a conversation
response = requests.post(
    "http://localhost:8000/chat",
    json={
        "message": "What do you think about investing in Apple?",
        "thread_id": "user_123"
    }
)
print(response.json())
```

### Screen for Quality Stocks
```python
# Find quality dividend stocks
response = requests.post(
    "http://localhost:8000/screen",
    json={
        "criteria": {
            "roe": {"min": 15},
            "debt_to_equity": {"max": 0.5},
            "dividend_yield": {"min": 2}
        }
    }
)
print(response.json())
```

## 🔄 LangGraph Workflow

The agent uses LangGraph to orchestrate a sophisticated analysis workflow:

1. **Input Processing**: Parse user queries and extract stock symbols
2. **Data Gathering**: Collect market data, fundamentals, and financial metrics
3. **Business Analysis**: Evaluate business quality and competitive advantages
4. **Financial Analysis**: Assess financial strength and stability
5. **Valuation**: Calculate intrinsic value and margin of safety
6. **Recommendation**: Generate investment recommendations with confidence levels
7. **Response**: Provide comprehensive analysis with clear reasoning

This modular approach ensures each step is transparent, auditable, and can be enhanced independently.