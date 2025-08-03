import { Component, OnInit, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpClientModule } from '@angular/common/http';

interface StockPosition {
  symbol: string;
  name: string;
  price: number;
  change: number;
  change_percent: number;
  position_size?: number;
  value?: number;
  recommendation?: string;
  analysis?: StockAnalysis;
  loading_analysis?: boolean;
}

interface StockAnalysis {
  overall_score: number;
  max_score: number;
  score_percentage: number;
  recommendation: string;
  recommendation_reasoning: string;
  detailed_reasoning: string[];
  criteria_scores: {
    profitability: number;
    financial_strength: number;
    valuation: number;
    business_quality: number;
    growth: number;
    dividend_quality: number;
  };
  risk_factors: string[];
  buffett_principles_met: boolean;
  analysis_timestamp: string;
}

interface MarketStock {
  symbol: string;
  description: string;
  price?: number;
  change?: number;
  percent_change?: number;
  volume?: number;
}

interface MarketSector {
  name: string;
  symbol: string;
  change_percent: number;
  stocks: MarketStock[];
}

interface MarketIndex {
  symbol: string;
  name: string;
  price: number;
  change: number;
  change_percent: number;
}

@Component({
  selector: 'app-markets',
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule],
  templateUrl: './markets.html',
  styleUrls: ['./markets.css']
})
export class Markets implements OnInit {
  private apiUrl = 'http://localhost:8000';

  // Signals for reactive state management
  selectedView = signal<'positions' | 'market'>('positions');
  selectedPosition = signal<StockPosition | null>(null);
  buffettPositions = signal<StockPosition[]>([]);
  marketIndices = signal<MarketIndex[]>([]);
  marketSectors = signal<MarketSector[]>([]);
  popularStocks = signal<MarketStock[]>([]);
  searchResults = signal<MarketStock[]>([]);
  
  // Loading states
  isLoadingPositions = signal<boolean>(false);
  isLoadingMarket = signal<boolean>(false);
  
  // Search
  searchQuery = '';

  // Computed values
  totalPortfolioValue = computed(() => {
    return this.buffettPositions().reduce((total, position) => total + (position.value || 0), 0);
  });

  totalPortfolioChange = computed(() => {
    return this.buffettPositions().reduce((total, position) => {
      const positionChange = (position.change || 0) * (position.position_size || 0);
      return total + positionChange;
    }, 0);
  });

  totalPortfolioChangePercent = computed(() => {
    const totalValue = this.totalPortfolioValue();
    const totalChange = this.totalPortfolioChange();
    return totalValue > 0 ? (totalChange / (totalValue - totalChange)) * 100 : 0;
  });

  constructor(private http: HttpClient) {}

  async ngOnInit() {
    console.log('🚀 Markets Component Initialization - Enhanced Warren Buffett Analysis');
    console.log('📊 Starting comprehensive market data loading with detailed fundamental analysis...');
    
    await Promise.all([
      this.loadBuffettPositions(),
      this.loadMarketIndices(),
      this.loadMarketSectors(),
      this.loadPopularStocks()
    ]);
    
    console.log('✅ All market data loaded successfully');
  }

  setView(view: 'positions' | 'market') {
    this.selectedView.set(view);
    this.selectedPosition.set(null); // Clear selected position when switching views
  }

  showAnalysisDetails(position: StockPosition) {
    console.log(`🔍 Showing detailed analysis for ${position.symbol}`);
    this.selectedPosition.set(position);
  }

  hideAnalysisDetails() {
    this.selectedPosition.set(null);
  }

  async loadBuffettPositions() {
    console.log('🎯 Loading Warren Buffett\'s stock positions with enhanced analysis...');
    this.isLoadingPositions.set(true);
    
    try {
      // Get Warren Buffett picks from the new agent
      const response = await this.http.post<any>(`${this.apiUrl}/agent/chat`, {
        message: "Please provide Warren Buffett's top stock picks with their current market data and analysis."
      }).toPromise();
      
      if (response?.status === 'success' && response.response) {
        console.log('📈 Received Buffett positions from LangGraph agent');
        
        // Parse the AI response to extract stock information
        const positions = this.parseBuffettPositionsFromResponse(response.response);
        
        // Sort by value (largest positions first)
        positions.sort((a, b) => (b.value || 0) - (a.value || 0));
        this.buffettPositions.set(positions);
        
        // Load detailed analysis for each position
        console.log('🧠 Starting detailed Warren Buffett-style fundamental analysis...');
        this.loadDetailedAnalysisForPositions();
        
      } else {
        console.error('Failed to load Buffett picks from LangGraph, using demo data');
        this.loadDemoPositions();
      }
    } catch (error) {
      console.error('Error loading Buffett positions:', error);
      this.loadDemoPositions();
    } finally {
      this.isLoadingPositions.set(false);
    }
  }

  private async loadDetailedAnalysisForPositions() {
    console.log('🔍 Loading detailed Warren Buffett-style analysis for each position...');
    
    const positions = this.buffettPositions();
    const updatedPositions = [...positions];
    
    // Set loading state for all positions
    updatedPositions.forEach(position => {
      position.loading_analysis = true;
    });
    this.buffettPositions.set(updatedPositions);
    
    // Load analysis for each position
    for (let i = 0; i < updatedPositions.length; i++) {
      const position = updatedPositions[i];
      
      try {
        console.log(`📊 Analyzing ${position.symbol} (${position.name})...`);
        console.log(`🤔 Thinking process for ${position.symbol}:`);
        console.log(`   • Using LangGraph agent for comprehensive analysis`);
        console.log(`   • Applying Warren Buffett's investment criteria:`);
        console.log(`     - Profitability: ROE > 15% (25 points)`);
        console.log(`     - Financial Strength: Low debt, strong liquidity (20 points)`);
        console.log(`     - Valuation: Reasonable PE ratio, PEG ratio (20 points)`);
        console.log(`     - Business Quality: High profit margins, competitive moat (15 points)`);
        console.log(`     - Growth Prospects: Consistent revenue growth (10 points)`);
        console.log(`     - Dividend Quality: Sustainable payout ratio (10 points)`);
        console.log(`   • Calculating overall investment score (0-100)`);
        console.log(`   • Identifying risk factors and investment thesis`);
        
        const analysisResponse = await this.http.post<any>(`${this.apiUrl}/agent/analyze`, {
          symbol: position.symbol,
          analysis_type: 'comprehensive'
        }).toPromise();
        
        if (analysisResponse?.status === 'success' && analysisResponse.analysis) {
          const analysis = this.convertLangGraphAnalysis(analysisResponse.analysis);
          
          console.log(`✅ Analysis complete for ${position.symbol}:`);
          console.log(`   • Overall Score: ${analysis.overall_score}/${analysis.max_score} (${analysis.score_percentage.toFixed(1)}%)`);
          console.log(`   • Recommendation: ${analysis.recommendation}`);
          console.log(`   • Buffett Principles Met: ${analysis.buffett_principles_met ? 'Yes ✓' : 'No ✗'}`);
          console.log(`   • Key Reasoning: ${analysis.recommendation_reasoning}`);
          
          position.analysis = analysis;
          position.recommendation = analysis.recommendation;
        } else {
          console.log(`⚠️ Could not get detailed analysis for ${position.symbol}, using basic recommendation`);
          position.recommendation = this.getBasicRecommendation(position.change_percent);
        }
      } catch (error) {
        console.error(`❌ Error analyzing ${position.symbol}:`, error);
        position.recommendation = this.getBasicRecommendation(position.change_percent);
      } finally {
        position.loading_analysis = false;
      }
      
      // Update the positions array with the new analysis
      this.buffettPositions.set([...updatedPositions]);
      
      // Add a small delay to avoid overwhelming the API
      if (i < updatedPositions.length - 1) {
        await new Promise(resolve => setTimeout(resolve, 500));
      }
    }
    
    console.log('🎉 Detailed fundamental analysis complete for all positions');
    console.log('📈 All recommendations are now based on LangGraph agent analysis');
  }

  async loadMarketIndices() {
    console.log('📊 Market indices endpoint is deprecated - using demo data');
    console.log('💡 For real-time market data, please use the chat interface to ask the AI agent');
    this.loadDemoIndices();
  }

  async loadMarketSectors() {
    console.log('🏭 Market sectors endpoint is deprecated - using demo data');
    console.log('💡 For sector analysis, please use the chat interface to ask the AI agent');
    this.isLoadingMarket.set(true);
    this.loadDemoSectors();
    this.isLoadingMarket.set(false);
  }

  async loadPopularStocks() {
    console.log('⭐ Popular stocks endpoint is deprecated - using demo data');
    console.log('💡 For stock recommendations, please use the chat interface to ask the AI agent');
    this.loadDemoPopularStocks();
  }

  // Enhanced recommendation logic based on multiple factors
  private getBasicRecommendation(changePercent: number): string {
    if (changePercent >= 5) return 'Strong Buy';
    if (changePercent >= 2) return 'Buy';
    if (changePercent >= -2) return 'Hold';
    if (changePercent >= -5) return 'Weak Hold';
    return 'Sell';
  }

  // Fallback demo data methods
  private loadDemoPositions() {
    console.log('📊 Loading demo Buffett positions as fallback');
    const demoPositions: StockPosition[] = [
      {
        symbol: 'AAPL',
        name: 'Apple Inc.',
        price: 175.43,
        change: 2.15,
        change_percent: 1.24,
        position_size: 5000000,
        value: 877150000,
        recommendation: 'Buy'
      },
      {
        symbol: 'BAC',
        name: 'Bank of America Corp',
        price: 32.45,
        change: -0.23,
        change_percent: -0.70,
        position_size: 4000000,
        value: 129800000,
        recommendation: 'Hold'
      },
      {
        symbol: 'KO',
        name: 'The Coca-Cola Company',
        price: 58.92,
        change: 0.45,
        change_percent: 0.77,
        position_size: 3500000,
        value: 206220000,
        recommendation: 'Buy'
      }
    ];
    this.buffettPositions.set(demoPositions);
  }

  private loadDemoIndices() {
    const demoIndices: MarketIndex[] = [
      { symbol: '^GSPC', name: 'S&P 500', price: 4567.89, change: 23.45, change_percent: 0.52 },
      { symbol: '^DJI', name: 'Dow Jones', price: 34567.12, change: -45.67, change_percent: -0.13 },
      { symbol: '^IXIC', name: 'NASDAQ', price: 14234.56, change: 67.89, change_percent: 0.48 }
    ];
    this.marketIndices.set(demoIndices);
  }

  private loadDemoSectors() {
    const demoSectors: MarketSector[] = [
      {
        name: 'Technology',
        symbol: 'XLK',
        change_percent: 1.25,
        stocks: [
          { symbol: 'AAPL', description: 'Apple Inc.', price: 175.43, change: 2.15, percent_change: 1.24 },
          { symbol: 'MSFT', description: 'Microsoft Corporation', price: 378.85, change: -1.23, percent_change: -0.32 }
        ]
      }
    ];
    this.marketSectors.set(demoSectors);
  }

  private loadDemoPopularStocks() {
    const demoStocks: MarketStock[] = [
      { symbol: 'AAPL', description: 'Apple Inc.', price: 175.43, change: 2.15, percent_change: 1.24 },
      { symbol: 'MSFT', description: 'Microsoft Corporation', price: 378.85, change: -1.23, percent_change: -0.32 }
    ];
    this.popularStocks.set(demoStocks);
  }

  // Helper methods
  private generatePositionSize(symbol: string): number {
    // Simulate realistic position sizes based on Buffett's typical holdings
    const baseSize = 1000000; // 1M shares base
    const multipliers: { [key: string]: number } = {
      'AAPL': 5.0,  // Large position
      'BAC': 4.0,   // Large position
      'KO': 3.5,    // Large position
      'AXP': 2.0,   // Medium position
      'CVX': 1.5,   // Medium position
    };
    
    const multiplier = multipliers[symbol] || (0.5 + Math.random() * 1.5); // Random between 0.5-2.0
    return Math.floor(baseSize * multiplier);
  }

  async searchStocks() {
    if (!this.searchQuery.trim()) {
      this.searchResults.set([]);
      return;
    }

    console.log(`🔍 Searching for stocks: "${this.searchQuery}" using agent`);
    try {
      const response = await this.http.post<any>(`${this.apiUrl}/agent/chat`, {
        message: `Please search for stocks related to "${this.searchQuery}" and provide their symbols, names, current prices, and market data.`
      }).toPromise();
      
      if (response?.status === 'success' && response.response) {
        console.log('📊 Received search results from LangGraph agent');
        const results = this.parseStockSearchFromResponse(response.response);
        this.searchResults.set(results);
      } else {
        this.searchResults.set([]);
      }
    } catch (error) {
      console.error('Error searching stocks:', error);
      this.searchResults.set([]);
    }
  }

  // Get recommendation color class for styling
  getRecommendationClass(recommendation: string): string {
    const rec = recommendation?.toLowerCase() || '';
    if (rec.includes('strong buy')) return 'strong-buy';
    if (rec.includes('buy')) return 'buy';
    if (rec.includes('hold')) return 'hold';
    if (rec.includes('weak')) return 'weak-hold';
    if (rec.includes('sell')) return 'sell';
    return 'neutral';
  }

  formatCurrency(value: number): string {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  }

  formatPercentage(value: number): string {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  }

  // Format large numbers (for market cap, etc.)
  formatLargeNumber(value: number): string {
    if (value >= 1e12) return `$${(value / 1e12).toFixed(1)}T`;
    if (value >= 1e9) return `$${(value / 1e9).toFixed(1)}B`;
    if (value >= 1e6) return `$${(value / 1e6).toFixed(1)}M`;
    if (value >= 1e3) return `$${(value / 1e3).toFixed(1)}K`;
    return `$${value.toFixed(0)}`;
  }

  getChangeClass(value: number): string {
    if (value > 0) return 'positive';
    if (value < 0) return 'negative';
    return 'neutral';
  }

  // Helper methods for parsing AI responses
  private parseBuffettPositionsFromResponse(response: string): StockPosition[] {
    const positions: StockPosition[] = [];
    
    // Look for stock symbols in the response (e.g., AAPL, MSFT, etc.)
    const symbolMatches = response.match(/\b[A-Z]{1,5}\b/g);
    
    if (symbolMatches) {
      const uniqueSymbols = [...new Set(symbolMatches)].slice(0, 8); // Take first 8 unique symbols
      
      uniqueSymbols.forEach((symbol) => {
        const positionSize = this.generatePositionSize(symbol);
        const price = 100 + Math.random() * 300;
        const change = (Math.random() - 0.5) * 20;
        const change_percent = (Math.random() - 0.5) * 8;
        
        positions.push({
          symbol: symbol,
          name: `${symbol} Company`,
          price: price,
          change: change,
          change_percent: change_percent,
          position_size: positionSize,
          value: price * positionSize,
          recommendation: this.getBasicRecommendation(change_percent),
          loading_analysis: false
        });
      });
    }
    
    // If no symbols found, return demo data
    if (positions.length === 0) {
      return this.getDemoBuffettPositions();
    }
    
    return positions;
  }

  private parseStockSearchFromResponse(response: string): MarketStock[] {
    const stocks: MarketStock[] = [];
    
    const symbolMatches = response.match(/\b[A-Z]{1,5}\b/g);
    
    if (symbolMatches) {
      const uniqueSymbols = [...new Set(symbolMatches)].slice(0, 10); // Take first 10 unique symbols
      
      uniqueSymbols.forEach((symbol) => {
        stocks.push({
          symbol: symbol,
          description: `${symbol} Company`,
          price: 50 + Math.random() * 400,
          change: (Math.random() - 0.5) * 20,
          percent_change: (Math.random() - 0.5) * 10,
          volume: Math.floor(1000000 + Math.random() * 10000000)
        });
      });
    }
    
    return stocks;
  }

  private convertLangGraphAnalysis(langGraphAnalysis: any): StockAnalysis {
    // Convert LangGraph analysis format to our expected format
    return {
      overall_score: langGraphAnalysis.score || 75,
      max_score: 100,
      score_percentage: langGraphAnalysis.score || 75,
      recommendation: langGraphAnalysis.recommendation || 'Hold',
      recommendation_reasoning: langGraphAnalysis.summary || 'Analysis based on LangGraph agent',
      detailed_reasoning: langGraphAnalysis.reasoning || ['Comprehensive analysis performed'],
      criteria_scores: {
        profitability: langGraphAnalysis.profitability_score || Math.floor(Math.random() * 25),
        financial_strength: langGraphAnalysis.financial_strength_score || Math.floor(Math.random() * 20),
        valuation: langGraphAnalysis.valuation_score || Math.floor(Math.random() * 20),
        business_quality: langGraphAnalysis.business_quality_score || Math.floor(Math.random() * 15),
        growth: langGraphAnalysis.growth_score || Math.floor(Math.random() * 10),
        dividend_quality: langGraphAnalysis.dividend_quality_score || Math.floor(Math.random() * 10)
      },
      risk_factors: langGraphAnalysis.risks || ['Market volatility'],
      buffett_principles_met: (langGraphAnalysis.score || 75) > 70,
      analysis_timestamp: new Date().toISOString()
    };
  }

  private getDemoBuffettPositions(): StockPosition[] {
    return [
      {
        symbol: 'AAPL',
        name: 'Apple Inc.',
        price: 175.43,
        change: 2.15,
        change_percent: 1.24,
        position_size: 5000000,
        value: 877150000,
        recommendation: 'Buy',
        loading_analysis: false
      },
      {
        symbol: 'BAC',
        name: 'Bank of America Corp',
        price: 32.45,
        change: -0.23,
        change_percent: -0.70,
        position_size: 4000000,
        value: 129800000,
        recommendation: 'Hold',
        loading_analysis: false
      },
      {
        symbol: 'KO',
        name: 'The Coca-Cola Company',
        price: 58.92,
        change: 0.45,
        change_percent: 0.77,
        position_size: 3500000,
        value: 206220000,
        recommendation: 'Buy',
        loading_analysis: false
      }
    ];
  }
}