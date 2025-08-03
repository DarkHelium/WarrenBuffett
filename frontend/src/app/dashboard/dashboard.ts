import { Component, OnInit, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpClientModule } from '@angular/common/http';

interface StockInfo {
  symbol: string;
  name: string;
  price: number;
  change: number;
  change_percent: number;
  market_cap?: number;
  pe_ratio?: number;
  dividend_yield?: number;
}

interface FinnhubStock {
  symbol: string;
  description: string;
  display_symbol?: string;
  type?: string;
  price?: number;
  change?: number;
  percent_change?: number;
  high?: number;
  low?: number;
}

interface PopularStock {
  symbol: string;
  description: string;
  price: number;
  change: number;
  percent_change: number;
  high: number;
  low: number;
}

interface FinnhubQuote {
  symbol: string;
  current_price: number;
  change: number;
  percent_change: number;
  high_price: number;
  low_price: number;
  open_price: number;
  previous_close: number;
}

interface BuffettScore {
  symbol: string;
  overall_score: number;
  criteria_scores: {
    economic_moat: number;
    financial_strength: number;
    management_quality: number;
    valuation: number;
    growth_prospects: number;
    dividend_consistency: number;
  };
  analysis: string;
  recommendation: string;
}

interface FinancialMetrics {
  market_cap?: number;
  pe_ratio?: number;
  pb_ratio?: number;
  debt_to_equity?: number;
  roe?: number;
  roa?: number;
  profit_margin?: number;
  revenue_growth?: number;
  dividend_yield?: number;
  free_cash_flow?: number;
}

interface StockAnalysis {
  symbol: string;
  company_name: string;
  current_price: number;
  buffett_score: BuffettScore;
  financial_metrics: FinancialMetrics;
  competitive_advantages: string[];
  risks: string[];
}

interface ChatMessage {
  message: string;
  timestamp?: Date;
}

interface ChatResponse {
  response: string;
  buffett_picks?: string[];
  timestamp: Date;
}

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule],
  templateUrl: './dashboard.html',
  styleUrls: ['./dashboard.css']
})
export class Dashboard implements OnInit {
  private apiUrl = 'http://localhost:8000';
  
  // Signals for reactive state management
  buffettPicks = signal<StockInfo[]>([]);
  selectedStock = signal<StockInfo | null>(null);
  stockAnalysis = signal<StockAnalysis | null>(null);
  isAnalyzing = signal(false);
  isAIScoring = signal(false);
  aiScore = signal<any>(null);
  
  // All stocks functionality
  allStocks = signal<FinnhubStock[]>([]);
  popularStocks = signal<PopularStock[]>([]);
  stockQuotes = signal<FinnhubQuote[]>([]);
  isLoadingAllStocks = signal(false);
  isLoadingPopularStocks = signal(false);
  currentView = signal<'buffett' | 'all' | 'popular'>('buffett');
  
  // Chat functionality
  chatMessages = signal<Array<{text: string, isUser: boolean, timestamp: Date}>>([]);
  currentMessage = signal('');
  
  // Search functionality
  searchQuery = signal('');
  searchResults = signal<StockInfo[]>([]);
  
  // Loading states
  isLoading = signal(true);
  isChatLoading = signal(false);
  
  constructor(private http: HttpClient) {}
  
  ngOnInit() {
    this.loadBuffettPicks();
    this.initializeChat();
  }
  
  async loadBuffettPicks() {
    try {
      this.isLoading.set(true);
      // Since /buffett-picks is deprecated, we'll use the LangGraph chat to get recommendations
      const response = await this.http.post<any>(`${this.apiUrl}/agent/chat`, {
        message: "What are your current top 5 stock picks with their current prices and brief analysis?"
      }).toPromise();
      
      if (response && response.status === 'success' && response.response) {
        // Parse the AI response to extract stock information
        const stockPicks = this.parseStockPicksFromResponse(response.response);
        this.buffettPicks.set(stockPicks);
      } else {
        console.error('AI agent did not return success, loading demo data.');
        this.loadDemoData();
      }
    } catch (error) {
      console.error('Error loading Buffett picks:', error);
      // Load demo data if API fails
      this.loadDemoData();
    } finally {
      this.isLoading.set(false);
    }
  }

  async loadAllStocks() {
    try {
      this.isLoadingAllStocks.set(true);
      // The /stocks/all endpoint is deprecated, so we'll show a message to users
      console.warn('All stocks endpoint is no longer available. Please use the chat interface to ask about specific stocks.');
      this.allStocks.set([]);
    } catch (error) {
      console.error('Error loading all stocks:', error);
    } finally {
      this.isLoadingAllStocks.set(false);
    }
  }

  async loadPopularStocks() {
    try {
      this.isLoadingPopularStocks.set(true);
      // The /stocks/popular endpoint is deprecated, so we'll show a message to users
      console.warn('Popular stocks endpoint is no longer available. Please use the chat interface to ask about popular stocks.');
      this.popularStocks.set([]);
    } catch (error) {
      console.error('Error loading popular stocks:', error);
    } finally {
      this.isLoadingPopularStocks.set(false);
    }
  }

  async loadStockQuotes(symbols: string) {
    try {
      // The /stocks/quotes endpoint is deprecated, so we'll show a message to users
      console.warn('Stock quotes endpoint is no longer available. Please use the chat interface to ask about specific stock prices.');
      this.stockQuotes.set([]);
    } catch (error) {
      console.error('Error loading stock quotes:', error);
    }
  }

  // View switching methods
  switchToBuffettView() {
    this.currentView.set('buffett');
  }

  switchToAllStocksView() {
    this.currentView.set('all');
    if (this.allStocks().length === 0) {
      this.loadAllStocks();
    }
  }

  switchToPopularStocksView() {
    this.currentView.set('popular');
    if (this.popularStocks().length === 0) {
      this.loadPopularStocks();
    }
  }

  // Helper method to get quote for a specific stock
  getQuoteForStock(symbol: string): FinnhubQuote | null {
    return this.stockQuotes().find(quote => quote.symbol === symbol) || null;
  }

  // Convert Finnhub stock to StockInfo for compatibility
  convertFinnhubToStockInfo(finnhubStock: FinnhubStock): StockInfo {
    const quote = this.getQuoteForStock(finnhubStock.symbol);
    return {
      symbol: finnhubStock.symbol,
      name: finnhubStock.description,
      price: quote?.current_price || 0,
      change: quote?.change || 0,
      change_percent: quote?.percent_change || 0,
      market_cap: undefined,
      pe_ratio: undefined,
      dividend_yield: undefined
    };
  }
  
  initializeChat() {
    const welcomeMessage = {
      text: "Hello! I'm Warren Buffett's AI assistant. I can help you understand my investment philosophy and analyze stocks using my criteria. What would you like to know?",
      isUser: false,
      timestamp: new Date()
    };
    this.chatMessages.set([welcomeMessage]);
  }
  
  selectStock(stock: StockInfo) {
    this.selectedStock.set(stock);
    this.stockAnalysis.set(null);
  }
  
  async analyzeStock(stock: StockInfo) {
    try {
      this.isAnalyzing.set(true);
      // Use the new LangGraph analyze endpoint
      const response = await this.http.post<any>(`${this.apiUrl}/agent/analyze`, {
        symbol: stock.symbol,
        analysis_type: 'comprehensive'
      }).toPromise();
      
      if (response && response.status === 'success') {
        // Convert the LangGraph response to our StockAnalysis format
        const analysis: StockAnalysis = {
          symbol: stock.symbol,
          company_name: stock.name,
          current_price: stock.price,
          buffett_score: {
            symbol: stock.symbol,
            overall_score: (response.business_quality_score + response.financial_strength_score + response.valuation_score) / 3 * 100,
            criteria_scores: {
              economic_moat: response.business_quality_score * 100,
              financial_strength: response.financial_strength_score * 100,
              management_quality: 75, // Default value
              valuation: response.valuation_score * 100,
              growth_prospects: 70, // Default value
              dividend_consistency: 65 // Default value
            },
            recommendation: response.recommendation || 'Hold',
            analysis: response.recommendation || 'Analysis completed using Warren Buffett principles.'
          },
          financial_metrics: {
            market_cap: stock.market_cap || 0,
            pe_ratio: stock.pe_ratio || 0,
            pb_ratio: 2.5,
            debt_to_equity: 0.3,
            roe: 0.25,
            roa: 0.15,
            profit_margin: 0.20,
            revenue_growth: 0.08,
            free_cash_flow: 50000000000,
            dividend_yield: stock.dividend_yield || 0
          },
          competitive_advantages: response.risk_factors ? ['Strong market position'] : ['Strong competitive advantages'],
          risks: response.risk_factors || ['General market risks']
        };
        
        this.stockAnalysis.set(analysis);
      } else {
        throw new Error(response?.error || 'Analysis failed');
      }
    } catch (error) {
      console.error('Error analyzing stock:', error);
      // Show demo analysis if API fails
      this.showDemoAnalysis(stock);
    } finally {
      this.isAnalyzing.set(false);
    }
  }

  async scoreWithBuffettAI(stock: StockInfo) {
    try {
      this.isAIScoring.set(true);
      
      // Use the new LangGraph chat endpoint for AI scoring
      const response = await this.http.post<any>(`${this.apiUrl}/agent/chat`, {
        message: `Please provide a comprehensive Warren Buffett-style analysis and score for ${stock.symbol} (${stock.name}). Include specific scoring criteria, competitive advantages, risks, and your recommendation.`
      }).toPromise();
      
      if (response && response.status === 'success' && response.response) {
        // Create a detailed analysis from the AI response
        const aiAnalysis: StockAnalysis = {
          symbol: stock.symbol,
          company_name: stock.name,
          current_price: stock.price,
          buffett_score: {
            symbol: stock.symbol,
            overall_score: this.extractScoreFromResponse(response.response),
            criteria_scores: {
              economic_moat: 85,
              financial_strength: 80,
              management_quality: 90,
              valuation: 75,
              growth_prospects: 70,
              dividend_consistency: 65
            },
            recommendation: this.extractRecommendationFromResponse(response.response),
            analysis: response.response
          },
          financial_metrics: {
            market_cap: stock.market_cap || 0,
            pe_ratio: stock.pe_ratio || 0,
            pb_ratio: 2.5,
            debt_to_equity: 0.3,
            roe: 0.25,
            roa: 0.15,
            profit_margin: 0.20,
            revenue_growth: 0.08,
            free_cash_flow: 50000000000,
            dividend_yield: stock.dividend_yield || 0
          },
          competitive_advantages: this.extractAdvantagesFromResponse(response.response),
          risks: this.extractRisksFromResponse(response.response)
        };
        
        this.stockAnalysis.set(aiAnalysis);
        this.aiScore.set(response);
      }
    } catch (error) {
      console.error('Error scoring with Buffett AI:', error);
      // Show demo AI analysis if API fails
      this.showDemoAIAnalysis(stock);
    } finally {
      this.isAIScoring.set(false);
    }
  }

  private extractScoreFromResponse(response: string): number {
    // Try to extract a numerical score from the response
    const scoreMatch = response.match(/score[:\s]*(\d+)/i) || response.match(/(\d+)\/100/i) || response.match(/(\d+)\s*out\s*of\s*100/i);
    if (scoreMatch) {
      return parseInt(scoreMatch[1]);
    }
    // Default score based on sentiment analysis
    if (response.toLowerCase().includes('strong buy') || response.toLowerCase().includes('excellent')) return 85;
    if (response.toLowerCase().includes('buy') || response.toLowerCase().includes('good')) return 75;
    if (response.toLowerCase().includes('hold') || response.toLowerCase().includes('average')) return 60;
    if (response.toLowerCase().includes('sell') || response.toLowerCase().includes('poor')) return 40;
    return 70; // Default moderate score
  }

  private extractRecommendationFromResponse(response: string): string {
    if (response.toLowerCase().includes('strong buy')) return 'Strong Buy';
    if (response.toLowerCase().includes('buy')) return 'Buy';
    if (response.toLowerCase().includes('hold')) return 'Hold';
    if (response.toLowerCase().includes('sell')) return 'Sell';
    return 'Hold';
  }

  private extractAdvantagesFromResponse(response: string): string[] {
    const advantages = [];
    if (response.toLowerCase().includes('moat') || response.toLowerCase().includes('competitive advantage')) {
      advantages.push('Strong competitive moat');
    }
    if (response.toLowerCase().includes('brand') || response.toLowerCase().includes('reputation')) {
      advantages.push('Strong brand recognition');
    }
    if (response.toLowerCase().includes('cash flow') || response.toLowerCase().includes('financial')) {
      advantages.push('Consistent cash flow generation');
    }
    if (response.toLowerCase().includes('management') || response.toLowerCase().includes('leadership')) {
      advantages.push('Excellent management team');
    }
    return advantages.length > 0 ? advantages : ['AI-identified competitive strengths'];
  }

  private extractRisksFromResponse(response: string): string[] {
    const risks = [];
    if (response.toLowerCase().includes('competition') || response.toLowerCase().includes('competitive')) {
      risks.push('Increasing competitive pressure');
    }
    if (response.toLowerCase().includes('regulation') || response.toLowerCase().includes('regulatory')) {
      risks.push('Regulatory challenges');
    }
    if (response.toLowerCase().includes('market') || response.toLowerCase().includes('economic')) {
      risks.push('Market volatility and economic uncertainty');
    }
    if (response.toLowerCase().includes('technology') || response.toLowerCase().includes('disruption')) {
      risks.push('Technology disruption risks');
    }
    return risks.length > 0 ? risks : ['General market and business risks'];
  }

  private showDemoAIAnalysis(stock: StockInfo) {
    const demoAnalysis: StockAnalysis = {
      symbol: stock.symbol,
      company_name: stock.name,
      current_price: stock.price,
      buffett_score: {
        symbol: stock.symbol,
        overall_score: 78,
        criteria_scores: {
          economic_moat: 85,
          financial_strength: 80,
          management_quality: 75,
          valuation: 70,
          growth_prospects: 80,
          dividend_consistency: 70
        },
        recommendation: 'Buy',
        analysis: `Based on my AI analysis of ${stock.name}, this company demonstrates several characteristics I value: strong competitive positioning, consistent profitability, and reasonable valuation. The company shows good financial health with manageable debt levels and strong cash generation capabilities. However, investors should monitor competitive dynamics and market conditions.`
      },
      financial_metrics: {
        market_cap: stock.market_cap || 0,
        pe_ratio: stock.pe_ratio || 0,
        pb_ratio: 2.8,
        debt_to_equity: 0.4,
        roe: 0.22,
        roa: 0.12,
        profit_margin: 0.18,
        revenue_growth: 0.06,
        free_cash_flow: 25000000000,
        dividend_yield: stock.dividend_yield || 0
      },
      competitive_advantages: [
        'Strong brand recognition and customer loyalty',
        'Efficient operational model',
        'Consistent cash flow generation',
        'Experienced management team'
      ],
      risks: [
        'Market competition intensification',
        'Economic downturn impact',
        'Regulatory changes',
        'Technology disruption potential'
      ]
    };
    
    this.stockAnalysis.set(demoAnalysis);
  }
  
  async sendChatMessage() {
    const message = this.currentMessage().trim();
    if (!message) return;
    
    // Add user message
    const userMessage = {
      text: message,
      isUser: true,
      timestamp: new Date()
    };
    
    this.chatMessages.update(messages => [...messages, userMessage]);
    this.currentMessage.set('');
    this.isChatLoading.set(true);
    
    try {
      const response = await this.http.post<any>(`${this.apiUrl}/agent/chat`, {
        message: message
      }).toPromise();
      
      const aiMessage = {
        text: response?.response || "I'm sorry, I couldn't process that request.",
        isUser: false,
        timestamp: new Date()
      };
      
      this.chatMessages.update(messages => [...messages, aiMessage]);
    } catch (error) {
      console.error('Error sending chat message:', error);
      const errorMessage = {
        text: "I'm having trouble connecting right now. Please try again later.",
        isUser: false,
        timestamp: new Date()
      };
      this.chatMessages.update(messages => [...messages, errorMessage]);
    } finally {
      this.isChatLoading.set(false);
    }
  }
  
  async searchStocks() {
    const query = this.searchQuery().trim();
    if (!query) {
      this.searchResults.set([]);
      return;
    }
    
    try {
      // Since the search endpoint is deprecated, we'll use the chat to search for stocks
      const response = await this.http.post<any>(`${this.apiUrl}/agent/chat`, {
        message: `Please search for stocks related to "${query}" and provide their symbols, names, and current information.`
      }).toPromise();
      
      if (response && response.status === 'success' && response.response) {
        // Parse the response to extract stock information
        const stocks = this.parseStockSearchFromResponse(response.response);
        this.searchResults.set(stocks);
      } else {
        this.searchResults.set([]);
      }
    } catch (error) {
      console.error('Error searching stocks:', error);
      this.searchResults.set([]);
    }
  }
  
  // Navigation methods
  closeStockDetail(): void {
    this.selectedStock.set(null);
    this.stockAnalysis.set(null);
  }
  
  // Helper methods
  formatCurrency(value: number | null | undefined): string {
    if (value === null || value === undefined) return 'N/A';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  }
  
  formatPercentage(value: number | null | undefined): string {
    if (value === null || value === undefined) return 'N/A';
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  }
  
  formatMarketCap(value: number | null | undefined): string {
    if (value === null || value === undefined) return 'N/A';
    if (value >= 1e12) return `$${(value / 1e12).toFixed(1)}T`;
    if (value >= 1e9) return `$${(value / 1e9).toFixed(1)}B`;
    if (value >= 1e6) return `$${(value / 1e6).toFixed(1)}M`;
    return `$${value.toFixed(0)}`;
  }

  getScoreColor(score: number): string {
    if (score >= 80) return '#22c55e';
    if (score >= 60) return '#eab308';
    if (score >= 40) return '#f97316';
    return '#ef4444';
  }
  
  getRecommendationColor(recommendation: string): string {
    switch (recommendation.toLowerCase()) {
      case 'strong buy':
      case 'buy':
        return '#22c55e';
      case 'hold':
        return '#eab308';
      case 'sell':
      case 'strong sell':
        return '#ef4444';
      default:
        return '#ffffff';
    }
  }

  // Type assertion helpers for template
  asNumber(value: any): number {
    return typeof value === 'number' ? value : 0;
  }

  asString(value: any): string {
    return typeof value === 'string' ? value : String(value || '');
  }

  getMetricEntries(metrics: FinancialMetrics): Array<{key: string, value: number | undefined}> {
    return Object.entries(metrics).map(([key, value]) => ({
      key,
      value: typeof value === 'number' ? value : undefined
    }));
  }

  // Helper methods for parsing AI responses
  private parseStockPicksFromResponse(response: string): StockInfo[] {
    // This is a simplified parser - in a real implementation, you might want to use more sophisticated parsing
    const stocks: StockInfo[] = [];
    
    // Look for stock symbols in the response (e.g., AAPL, MSFT, etc.)
    const symbolMatches = response.match(/\b[A-Z]{1,5}\b/g);
    
    if (symbolMatches) {
      const uniqueSymbols = [...new Set(symbolMatches)].slice(0, 5); // Take first 5 unique symbols
      
      uniqueSymbols.forEach((symbol, index) => {
        stocks.push({
          symbol: symbol,
          name: `${symbol} Company`, // Placeholder name
          price: 100 + Math.random() * 200, // Random price for demo
          change: (Math.random() - 0.5) * 10,
          change_percent: (Math.random() - 0.5) * 5,
          market_cap: 1000000000 + Math.random() * 2000000000000,
          pe_ratio: 15 + Math.random() * 20,
          dividend_yield: Math.random() * 0.05
        });
      });
    }
    
    // If no symbols found, return demo data
    if (stocks.length === 0) {
      return this.getDemoStocks();
    }
    
    return stocks;
  }

  private parseStockSearchFromResponse(response: string): StockInfo[] {
    // Similar parsing logic for search results
    const stocks: StockInfo[] = [];
    
    const symbolMatches = response.match(/\b[A-Z]{1,5}\b/g);
    
    if (symbolMatches) {
      const uniqueSymbols = [...new Set(symbolMatches)].slice(0, 10); // Take first 10 unique symbols
      
      uniqueSymbols.forEach((symbol) => {
        stocks.push({
          symbol: symbol,
          name: `${symbol} Company`,
          price: 50 + Math.random() * 300,
          change: (Math.random() - 0.5) * 15,
          change_percent: (Math.random() - 0.5) * 8,
          market_cap: 500000000 + Math.random() * 1500000000000,
          pe_ratio: 10 + Math.random() * 25,
          dividend_yield: Math.random() * 0.06
        });
      });
    }
    
    return stocks;
  }

  private getDemoStocks(): StockInfo[] {
    return [
      {
        symbol: 'AAPL',
        name: 'Apple Inc.',
        price: 195.89,
        change: 2.34,
        change_percent: 1.21,
        market_cap: 3000000000000,
        pe_ratio: 29.5,
        dividend_yield: 0.0044
      },
      {
        symbol: 'BRK-B',
        name: 'Berkshire Hathaway Inc.',
        price: 348.50,
        change: -1.25,
        change_percent: -0.36,
        market_cap: 750000000000,
        pe_ratio: 15.2,
        dividend_yield: undefined
      },
      {
        symbol: 'KO',
        name: 'The Coca-Cola Company',
        price: 58.75,
        change: 0.85,
        change_percent: 1.47,
        market_cap: 254000000000,
        pe_ratio: 25.8,
        dividend_yield: 0.031
      }
    ];
  }
  
  private loadDemoData() {
    const demoStocks: StockInfo[] = [
      {
        symbol: 'AAPL',
        name: 'Apple Inc.',
        price: 195.89,
        change: 2.34,
        change_percent: 1.21,
        market_cap: 3000000000000,
        pe_ratio: 29.5,
        dividend_yield: 0.0044
      },
      {
        symbol: 'BRK-B',
        name: 'Berkshire Hathaway Inc.',
        price: 348.50,
        change: -1.25,
        change_percent: -0.36,
        market_cap: 750000000000,
        pe_ratio: 15.2,
        dividend_yield: undefined
      },
      {
        symbol: 'KO',
        name: 'The Coca-Cola Company',
        price: 58.75,
        change: 0.85,
        change_percent: 1.47,
        market_cap: 254000000000,
        pe_ratio: 25.8,
        dividend_yield: 0.031
      }
    ];
    this.buffettPicks.set(demoStocks);
  }
  
  private showDemoAnalysis(stock: StockInfo) {
    const demoAnalysis: StockAnalysis = {
      symbol: stock.symbol,
      company_name: stock.name,
      current_price: stock.price,
      buffett_score: {
        symbol: stock.symbol,
        overall_score: 78.5,
        criteria_scores: {
          economic_moat: 85,
          financial_strength: 82,
          management_quality: 75,
          valuation: 65,
          growth_prospects: 70,
          dividend_consistency: 80
        },
        analysis: `Analysis of ${stock.name} (${stock.symbol}) through Warren Buffett's lens:\n\n🏰 STRONG ECONOMIC MOAT: This company demonstrates exceptional competitive advantages. The balance sheet is fortress-like with minimal debt and strong cash position. Reasonably valued given the company's fundamentals. Competent management team with decent track record.`,
        recommendation: 'BUY - Good value investment with solid fundamentals'
      },
      financial_metrics: {
        market_cap: stock.market_cap,
        pe_ratio: stock.pe_ratio,
        pb_ratio: 5.2,
        debt_to_equity: 45.3,
        roe: 0.18,
        roa: 0.12,
        profit_margin: 0.25,
        revenue_growth: 0.08,
        dividend_yield: stock.dividend_yield,
        free_cash_flow: 95000000000
      },
      competitive_advantages: [
        'Strong brand recognition and customer loyalty',
        'Significant barriers to entry in the industry',
        'High profit margins indicating pricing power'
      ],
      risks: [
        'High valuation may limit upside potential',
        'Regulatory risks in key markets'
      ]
    };
    this.stockAnalysis.set(demoAnalysis);
  }
}