"""
LLM Analysis Module
Generates insights and analysis using Large Language Models (OpenAI, Perplexity).
"""

import os
import json
import requests
from typing import List, Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMAnalyzer:
    """Analyzes market data using Large Language Models."""
    
    def __init__(self):
        self.openai_api_key = os.environ.get('OPENAI_API_KEY')
        self.perplexity_api_key = os.environ.get('PERPLEXITY_API_KEY')
        
    def analyze_with_openai(self, prompt: str, model: str = "gpt-4") -> Optional[str]:
        """Generate analysis using OpenAI API."""
        if not self.openai_api_key:
            logger.warning("OpenAI API key not set")
            return None
        
        try:
            headers = {
                'Authorization': f'Bearer {self.openai_api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': model,
                'messages': [
                    {'role': 'system', 'content': 'You are a financial analyst expert providing concise, actionable market insights.'},
                    {'role': 'user', 'content': prompt}
                ],
                'temperature': 0.7,
                'max_tokens': 1500
            }
            
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            
            return response.json()['choices'][0]['message']['content']
        
        except Exception as e:
            logger.error(f"Error with OpenAI API: {e}")
            return None
    
    def analyze_with_perplexity(self, query: str) -> Optional[str]:
        """Generate analysis using Perplexity API for real-time web search."""
        if not self.perplexity_api_key:
            logger.warning("Perplexity API key not set")
            return None
        
        try:
            headers = {
                'Authorization': f'Bearer {self.perplexity_api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'pplx-70b-online',
                'messages': [
                    {'role': 'system', 'content': 'You are a financial analyst providing real-time market insights.'},
                    {'role': 'user', 'content': query}
                ]
            }
            
            response = requests.post(
                'https://api.perplexity.ai/chat/completions',
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            
            return response.json()['choices'][0]['message']['content']
        
        except Exception as e:
            logger.error(f"Error with Perplexity API: {e}")
            return None
    
    def generate_market_summary(self, news_articles: List[Dict[str, Any]], market_data: Dict[str, Any]) -> str:
        """Generate comprehensive market summary from news and data."""
        # Prepare context
        news_summary = "\n".join([
            f"- {article.get('title', 'N/A')}" 
            for article in news_articles[:10]
        ])
        
        prompt = f"""
Based on the following market information, provide a concise executive summary:

LATEST NEWS:
{news_summary}

MARKET DATA:
{json.dumps(market_data, indent=2)}

Provide:
1. Key market themes (2-3 sentences)
2. Major risks and opportunities
3. Actionable insights for investors

Keep it under 300 words.
"""
        
        # Try Perplexity first for real-time context, fallback to OpenAI
        result = self.analyze_with_perplexity(prompt)
        if not result:
            result = self.analyze_with_openai(prompt)
        
        return result or "Unable to generate analysis at this time."
    
    def analyze_turkish_market(self, bist_data: Dict[str, Any], economic_indicators: Dict[str, Any]) -> str:
        """Generate analysis specific to Turkish markets."""
        prompt = f"""
Analyze the Turkish market (BIST) given the following data:

BIST INDEX DATA:
{json.dumps(bist_data, indent=2)}

ECONOMIC INDICATORS:
{json.dumps(economic_indicators, indent=2)}

Focus on:
1. TCMB (Central Bank) policy impact
2. Inflation trends
3. TRY currency movements
4. Sector-specific opportunities
5. Key risks for Turkish investors

Provide actionable insights in 250 words.
"""
        
        result = self.analyze_with_openai(prompt)
        return result or "Unable to generate Turkish market analysis."
    
    def generate_sector_analysis(self, sector: str, sector_data: Dict[str, Any]) -> str:
        """Generate deep-dive analysis for a specific sector."""
        prompt = f"""
Analyze the {sector} sector based on the following data:

{json.dumps(sector_data, indent=2)}

Provide:
1. Current sector sentiment and trends
2. Top performers and laggards
3. Catalysts to watch
4. Investment recommendation (Overweight/Neutral/Underweight)

Keep it concise (200 words max).
"""
        
        return self.analyze_with_openai(prompt) or f"Unable to analyze {sector} sector."
    
    def explain_regime_change(self, regime_data: Dict[str, Any]) -> str:
        """Explain macro regime changes and implications."""
        prompt = f"""
Explain the current macro regime and what it means for investors:

{json.dumps(regime_data, indent=2)}

Include:
1. What this regime means
2. Historical context
3. Best asset classes for this environment
4. Risk management strategies

Explain in simple terms (250 words).
"""
        
        return self.analyze_with_openai(prompt) or "Unable to explain regime change."


if __name__ == "__main__":
    analyzer = LLMAnalyzer()
    test_prompt = "Summarize the current market conditions in 100 words."
    result = analyzer.analyze_with_openai(test_prompt)
    print(result)
