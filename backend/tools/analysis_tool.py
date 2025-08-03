"""
Analysis Tool for Warren Buffett Stock Analysis Agent
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from core.config import Config

logger = logging.getLogger(__name__)


class AnalysisTool:
    """
    Tool for performing stock analysis using Warren Buffett's principles.
    
    This tool provides various analysis functions including:
    - Business quality assessment
    - Financial strength evaluation
    - Valuation analysis
    - Risk assessment
    """
    
    def __init__(self, config: Config):
        """Initialize the analysis tool."""
        self.config = config
        logger.info("Analysis Tool initialized")
    
    def analyze_business_quality(self, fundamentals: Dict, profile: Dict) -> Dict[str, Any]:
        """
        Analyze business quality using Warren Buffett's criteria.
        
        Args:
            fundamentals: Financial metrics
            profile: Company profile information
            
        Returns:
            Business quality assessment
        """
        try:
            metrics = fundamentals.get('fundamentals', {})
            company_info = profile.get('profile', {})
            
            # ROE Analysis (Warren looks for consistent ROE > 15%)
            roe = metrics.get('roe', 0)
            roe_score = self._score_roe(roe)
            
            # Profit Margin Analysis
            net_margin = metrics.get('net_margin', 0)
            margin_score = self._score_profit_margin(net_margin)
            
            # Debt Analysis (Warren prefers low debt)
            debt_to_equity = metrics.get('debt_to_equity', 0)
            debt_score = self._score_debt_level(debt_to_equity)
            
            # Consistency Analysis (based on available growth metrics)
            revenue_growth_3y = metrics.get('revenue_growth_3y', 0)
            eps_growth_3y = metrics.get('eps_growth_3y', 0)
            consistency_score = self._score_consistency(revenue_growth_3y, eps_growth_3y)
            
            # Overall business quality score
            overall_score = (roe_score + margin_score + debt_score + consistency_score) / 4
            
            return {
                'overall_score': overall_score,
                'roe_analysis': {
                    'value': roe,
                    'score': roe_score,
                    'assessment': self._assess_roe(roe)
                },
                'profitability_analysis': {
                    'net_margin': net_margin,
                    'score': margin_score,
                    'assessment': self._assess_profit_margin(net_margin)
                },
                'debt_analysis': {
                    'debt_to_equity': debt_to_equity,
                    'score': debt_score,
                    'assessment': self._assess_debt_level(debt_to_equity)
                },
                'consistency_analysis': {
                    'revenue_growth_3y': revenue_growth_3y,
                    'eps_growth_3y': eps_growth_3y,
                    'score': consistency_score,
                    'assessment': self._assess_consistency(revenue_growth_3y, eps_growth_3y)
                },
                'industry': company_info.get('industry', 'Unknown'),
                'market_cap': company_info.get('market_cap', 0)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing business quality: {str(e)}")
            return {'error': str(e)}
    
    def analyze_valuation(self, fundamentals: Dict, quote: Dict) -> Dict[str, Any]:
        """
        Analyze stock valuation using Warren Buffett's methods.
        
        Args:
            fundamentals: Financial metrics
            quote: Current stock quote
            
        Returns:
            Valuation analysis
        """
        try:
            metrics = fundamentals.get('fundamentals', {})
            current_price = quote.get('quote', {}).get('current_price', 0)
            
            # P/E Ratio Analysis
            pe_ratio = metrics.get('pe_ratio', 0)
            pe_score = self._score_pe_ratio(pe_ratio)
            
            # P/B Ratio Analysis
            pb_ratio = metrics.get('pb_ratio', 0)
            pb_score = self._score_pb_ratio(pb_ratio)
            
            # PEG Ratio Analysis
            peg_ratio = metrics.get('peg_ratio', 0)
            peg_score = self._score_peg_ratio(peg_ratio)
            
            # Dividend Yield Analysis
            dividend_yield = metrics.get('dividend_yield', 0)
            dividend_score = self._score_dividend_yield(dividend_yield)
            
            # Overall valuation score
            valuation_score = (pe_score + pb_score + peg_score + dividend_score) / 4
            
            # Estimate intrinsic value (simplified DCF approach)
            estimated_intrinsic_value = self._estimate_intrinsic_value(metrics, current_price)
            
            # Margin of safety
            margin_of_safety = self._calculate_margin_of_safety(current_price, estimated_intrinsic_value)
            
            return {
                'valuation_score': valuation_score,
                'current_price': current_price,
                'estimated_intrinsic_value': estimated_intrinsic_value,
                'margin_of_safety': margin_of_safety,
                'pe_analysis': {
                    'value': pe_ratio,
                    'score': pe_score,
                    'assessment': self._assess_pe_ratio(pe_ratio)
                },
                'pb_analysis': {
                    'value': pb_ratio,
                    'score': pb_score,
                    'assessment': self._assess_pb_ratio(pb_ratio)
                },
                'peg_analysis': {
                    'value': peg_ratio,
                    'score': peg_score,
                    'assessment': self._assess_peg_ratio(peg_ratio)
                },
                'dividend_analysis': {
                    'yield': dividend_yield,
                    'score': dividend_score,
                    'assessment': self._assess_dividend_yield(dividend_yield)
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing valuation: {str(e)}")
            return {'error': str(e)}
    
    def analyze_financial_strength(self, fundamentals: Dict) -> Dict[str, Any]:
        """
        Analyze financial strength using Warren Buffett's criteria.
        
        Args:
            fundamentals: Financial metrics
            
        Returns:
            Financial strength analysis
        """
        try:
            metrics = fundamentals.get('fundamentals', {})
            
            # Current Ratio Analysis
            current_ratio = metrics.get('current_ratio', 0)
            liquidity_score = self._score_current_ratio(current_ratio)
            
            # Debt to Equity Analysis
            debt_to_equity = metrics.get('debt_to_equity', 0)
            leverage_score = self._score_debt_level(debt_to_equity)
            
            # Return on Assets
            roa = metrics.get('roa', 0)
            efficiency_score = self._score_roa(roa)
            
            # Overall financial strength
            financial_strength = (liquidity_score + leverage_score + efficiency_score) / 3
            
            return {
                'financial_strength_score': financial_strength,
                'liquidity_analysis': {
                    'current_ratio': current_ratio,
                    'score': liquidity_score,
                    'assessment': self._assess_current_ratio(current_ratio)
                },
                'leverage_analysis': {
                    'debt_to_equity': debt_to_equity,
                    'score': leverage_score,
                    'assessment': self._assess_debt_level(debt_to_equity)
                },
                'efficiency_analysis': {
                    'roa': roa,
                    'score': efficiency_score,
                    'assessment': self._assess_roa(roa)
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing financial strength: {str(e)}")
            return {'error': str(e)}
    
    def generate_investment_recommendation(self, business_quality: Dict, valuation: Dict, 
                                         financial_strength: Dict) -> Dict[str, Any]:
        """
        Generate investment recommendation based on all analyses.
        
        Args:
            business_quality: Business quality analysis
            valuation: Valuation analysis
            financial_strength: Financial strength analysis
            
        Returns:
            Investment recommendation
        """
        try:
            # Calculate overall score
            bq_score = business_quality.get('overall_score', 0)
            val_score = valuation.get('valuation_score', 0)
            fs_score = financial_strength.get('financial_strength_score', 0)
            
            overall_score = (bq_score + val_score + fs_score) / 3
            
            # Margin of safety consideration
            margin_of_safety = valuation.get('margin_of_safety', 0)
            
            # Generate recommendation
            recommendation = self._generate_recommendation(overall_score, margin_of_safety)
            
            # Risk assessment
            risks = self._assess_risks(business_quality, valuation, financial_strength)
            
            return {
                'overall_score': overall_score,
                'recommendation': recommendation['action'],
                'confidence': recommendation['confidence'],
                'reasoning': recommendation['reasoning'],
                'target_price_range': recommendation['target_price_range'],
                'time_horizon': recommendation['time_horizon'],
                'key_risks': risks,
                'margin_of_safety': margin_of_safety,
                'component_scores': {
                    'business_quality': bq_score,
                    'valuation': val_score,
                    'financial_strength': fs_score
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating investment recommendation: {str(e)}")
            return {'error': str(e)}
    
    # Scoring methods (0-100 scale)
    def _score_roe(self, roe: float) -> float:
        """Score ROE (Return on Equity)."""
        if roe >= 20:
            return 100
        elif roe >= 15:
            return 80
        elif roe >= 10:
            return 60
        elif roe >= 5:
            return 40
        else:
            return 20
    
    def _score_profit_margin(self, margin: float) -> float:
        """Score profit margin."""
        if margin >= 20:
            return 100
        elif margin >= 15:
            return 80
        elif margin >= 10:
            return 60
        elif margin >= 5:
            return 40
        else:
            return 20
    
    def _score_debt_level(self, debt_to_equity: float) -> float:
        """Score debt level (lower is better)."""
        if debt_to_equity <= 0.3:
            return 100
        elif debt_to_equity <= 0.5:
            return 80
        elif debt_to_equity <= 1.0:
            return 60
        elif debt_to_equity <= 2.0:
            return 40
        else:
            return 20
    
    def _score_consistency(self, revenue_growth: float, eps_growth: float) -> float:
        """Score consistency of growth."""
        avg_growth = (revenue_growth + eps_growth) / 2
        if avg_growth >= 10 and revenue_growth > 0 and eps_growth > 0:
            return 100
        elif avg_growth >= 5 and revenue_growth > 0 and eps_growth > 0:
            return 80
        elif avg_growth >= 0:
            return 60
        else:
            return 40
    
    def _score_pe_ratio(self, pe: float) -> float:
        """Score P/E ratio."""
        if pe <= 0:
            return 20
        elif pe <= 15:
            return 100
        elif pe <= 20:
            return 80
        elif pe <= 25:
            return 60
        elif pe <= 35:
            return 40
        else:
            return 20
    
    def _score_pb_ratio(self, pb: float) -> float:
        """Score P/B ratio."""
        if pb <= 0:
            return 20
        elif pb <= 1.5:
            return 100
        elif pb <= 2.5:
            return 80
        elif pb <= 4.0:
            return 60
        else:
            return 40
    
    def _score_peg_ratio(self, peg: float) -> float:
        """Score PEG ratio."""
        if peg <= 0:
            return 20
        elif peg <= 1.0:
            return 100
        elif peg <= 1.5:
            return 80
        elif peg <= 2.0:
            return 60
        else:
            return 40
    
    def _score_dividend_yield(self, yield_pct: float) -> float:
        """Score dividend yield."""
        if yield_pct >= 4:
            return 100
        elif yield_pct >= 2:
            return 80
        elif yield_pct >= 1:
            return 60
        elif yield_pct > 0:
            return 40
        else:
            return 20
    
    def _score_current_ratio(self, ratio: float) -> float:
        """Score current ratio."""
        if ratio >= 2.0:
            return 100
        elif ratio >= 1.5:
            return 80
        elif ratio >= 1.0:
            return 60
        else:
            return 40
    
    def _score_roa(self, roa: float) -> float:
        """Score Return on Assets."""
        if roa >= 10:
            return 100
        elif roa >= 7:
            return 80
        elif roa >= 5:
            return 60
        elif roa >= 2:
            return 40
        else:
            return 20
    
    # Assessment methods
    def _assess_roe(self, roe: float) -> str:
        """Assess ROE quality."""
        if roe >= 20:
            return "Excellent - Very high returns on shareholder equity"
        elif roe >= 15:
            return "Good - Strong returns on equity"
        elif roe >= 10:
            return "Average - Moderate returns"
        else:
            return "Poor - Low returns on equity"
    
    def _assess_profit_margin(self, margin: float) -> str:
        """Assess profit margin quality."""
        if margin >= 15:
            return "Excellent - High profitability"
        elif margin >= 10:
            return "Good - Solid profit margins"
        elif margin >= 5:
            return "Average - Moderate profitability"
        else:
            return "Poor - Low profit margins"
    
    def _assess_debt_level(self, debt_to_equity: float) -> str:
        """Assess debt level."""
        if debt_to_equity <= 0.3:
            return "Excellent - Very low debt"
        elif debt_to_equity <= 0.5:
            return "Good - Manageable debt levels"
        elif debt_to_equity <= 1.0:
            return "Average - Moderate debt"
        else:
            return "Poor - High debt levels"
    
    def _assess_consistency(self, revenue_growth: float, eps_growth: float) -> str:
        """Assess growth consistency."""
        if revenue_growth > 0 and eps_growth > 0:
            return "Good - Consistent positive growth"
        elif revenue_growth > 0 or eps_growth > 0:
            return "Mixed - Some growth areas"
        else:
            return "Poor - Declining metrics"
    
    def _assess_pe_ratio(self, pe: float) -> str:
        """Assess P/E ratio."""
        if pe <= 15:
            return "Attractive - Low valuation"
        elif pe <= 25:
            return "Fair - Reasonable valuation"
        else:
            return "Expensive - High valuation"
    
    def _assess_pb_ratio(self, pb: float) -> str:
        """Assess P/B ratio."""
        if pb <= 1.5:
            return "Attractive - Trading below book value"
        elif pb <= 3.0:
            return "Fair - Reasonable book value multiple"
        else:
            return "Expensive - High book value multiple"
    
    def _assess_peg_ratio(self, peg: float) -> str:
        """Assess PEG ratio."""
        if peg <= 1.0:
            return "Attractive - Growth at reasonable price"
        elif peg <= 2.0:
            return "Fair - Moderate growth premium"
        else:
            return "Expensive - High growth premium"
    
    def _assess_dividend_yield(self, yield_pct: float) -> str:
        """Assess dividend yield."""
        if yield_pct >= 3:
            return "Good - Attractive dividend yield"
        elif yield_pct >= 1:
            return "Moderate - Some dividend income"
        else:
            return "Low - Minimal dividend income"
    
    def _assess_current_ratio(self, ratio: float) -> str:
        """Assess current ratio."""
        if ratio >= 2.0:
            return "Strong - Excellent liquidity"
        elif ratio >= 1.5:
            return "Good - Adequate liquidity"
        elif ratio >= 1.0:
            return "Acceptable - Minimal liquidity"
        else:
            return "Poor - Liquidity concerns"
    
    def _assess_roa(self, roa: float) -> str:
        """Assess Return on Assets."""
        if roa >= 10:
            return "Excellent - Very efficient asset use"
        elif roa >= 5:
            return "Good - Efficient operations"
        else:
            return "Poor - Inefficient asset utilization"
    
    def _estimate_intrinsic_value(self, metrics: Dict, current_price: float) -> float:
        """Estimate intrinsic value using simplified DCF."""
        try:
            # Simplified intrinsic value calculation
            # This is a basic implementation - in practice, you'd want more sophisticated DCF
            pe_ratio = metrics.get('pe_ratio', 0)
            roe = metrics.get('roe', 0)
            
            if pe_ratio > 0 and roe > 0:
                # Estimate fair P/E based on ROE and growth
                fair_pe = min(roe, 25)  # Cap at 25
                earnings_per_share = current_price / pe_ratio if pe_ratio > 0 else 0
                estimated_value = earnings_per_share * fair_pe
                return max(estimated_value, current_price * 0.5)  # Minimum 50% of current price
            else:
                return current_price  # Fallback to current price
                
        except Exception:
            return current_price
    
    def _calculate_margin_of_safety(self, current_price: float, intrinsic_value: float) -> float:
        """Calculate margin of safety percentage."""
        if intrinsic_value > 0:
            return ((intrinsic_value - current_price) / intrinsic_value) * 100
        return 0
    
    def _generate_recommendation(self, overall_score: float, margin_of_safety: float) -> Dict[str, Any]:
        """Generate investment recommendation."""
        if overall_score >= 80 and margin_of_safety >= 20:
            return {
                'action': 'Strong Buy',
                'confidence': 'High',
                'reasoning': 'Excellent business with attractive valuation and good margin of safety',
                'target_price_range': 'Current price + 20-40%',
                'time_horizon': '3-5 years'
            }
        elif overall_score >= 70 and margin_of_safety >= 10:
            return {
                'action': 'Buy',
                'confidence': 'Medium-High',
                'reasoning': 'Good business with reasonable valuation',
                'target_price_range': 'Current price + 10-25%',
                'time_horizon': '2-4 years'
            }
        elif overall_score >= 60:
            return {
                'action': 'Hold/Watch',
                'confidence': 'Medium',
                'reasoning': 'Decent business but wait for better entry point',
                'target_price_range': 'Wait for 10-20% decline',
                'time_horizon': '1-3 years'
            }
        else:
            return {
                'action': 'Avoid',
                'confidence': 'High',
                'reasoning': 'Poor business fundamentals or overvalued',
                'target_price_range': 'Not recommended',
                'time_horizon': 'N/A'
            }
    
    def _assess_risks(self, business_quality: Dict, valuation: Dict, financial_strength: Dict) -> List[str]:
        """Assess key investment risks."""
        risks = []
        
        # Business quality risks
        if business_quality.get('overall_score', 0) < 60:
            risks.append("Poor business fundamentals")
        
        # Valuation risks
        if valuation.get('margin_of_safety', 0) < 0:
            risks.append("Overvalued - no margin of safety")
        
        # Financial strength risks
        debt_analysis = business_quality.get('debt_analysis', {})
        if debt_analysis.get('score', 0) < 60:
            risks.append("High debt levels")
        
        # Liquidity risks
        liquidity_analysis = financial_strength.get('liquidity_analysis', {})
        if liquidity_analysis.get('score', 0) < 60:
            risks.append("Poor liquidity position")
        
        return risks if risks else ["Standard market risks"]