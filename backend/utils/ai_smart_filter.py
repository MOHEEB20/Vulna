"""AI-Powered Smart URL Filtering System"""

import asyncio
import json
import re
from typing import Dict, List, Tuple, Optional, Any
from urllib.parse import urlparse
import httpx


class AISmartFilter:
    """AI-powered intelligent URL filtering for penetration testing"""
    
    def __init__(self, ollama_host: str = "localhost", ollama_port: int = 11434):
        self.ollama_url = f"http://{ollama_host}:{ollama_port}/api/generate"
        self.filter_cache = {}
        self.cache_size_limit = 1000
        
        # Learning system for filter improvements
        self.learning_data = {
            "filtered_domains": [],
            "analyzed_domains": [],
            "false_positives": [],
            "user_feedback": []
        }
    
    async def should_analyze_url(self, url: str, method: str = "GET", headers: Dict = None) -> Dict[str, Any]:
        """
        AI-powered decision whether to analyze a URL.
        Returns detailed analysis with reasoning.
        """
        
        # Generate cache key
        cache_key = f"{method}:{url[:100]}"  # Limit URL length for cache
        if cache_key in self.filter_cache:
            return self.filter_cache[cache_key]
        
        # AI analysis
        result = await self._ai_url_analysis(url, method, headers or {})
        
        # Cache result (with size limit)
        if len(self.filter_cache) >= self.cache_size_limit:
            # Remove oldest entries
            oldest_keys = list(self.filter_cache.keys())[:100]
            for key in oldest_keys:
                del self.filter_cache[key]
        
        self.filter_cache[cache_key] = result
        return result
    
    async def _ai_url_analysis(self, url: str, method: str, headers: Dict) -> Dict[str, Any]:
        """Use AI to analyze if URL is worth pentesting"""
        
        parsed = urlparse(url)
        domain = parsed.netloc
        path = parsed.path
        query = parsed.query
        
        # Create AI prompt for URL analysis
        analysis_prompt = f"""
Du bist ein Experte für Penetration Testing und URL-Analyse. Analysiere diese URL und entscheide ob sie für Security Testing relevant ist.

URL: {url}
Method: {method}
Domain: {domain}
Path: {path}
Query: {query}
Headers: {json.dumps(headers, indent=2)}

ANALYSE-KRITERIEN:
1. Ist das eine CDN/Script-Provider Domain? (Google, Cloudflare, JScdn, etc.)
2. Ist das ein statisches Asset? (.js, .css, .png, .jpg, etc.)
3. Ist das eine sinnlose URL? (YouTube nocookie, Analytics, Ads, etc.)
4. Hat die URL Penetration Testing Potenzial? (APIs, Admin, Auth, Dynamic Content)
5. Ist die URL security-relevant für Web Application Testing?

BEWERTUNG:
- FILTER: Wenn CDN, statisch, sinnlos oder nicht security-relevant
- ANALYZE: Wenn API, Admin, Auth, Dynamic, Parameters, oder potenzielle Vulnerabilities

Antworte in JSON Format:
{{
    "decision": "FILTER" oder "ANALYZE",
    "confidence": 0.0-1.0,
    "reasoning": "Kurze Begründung auf Deutsch",
    "category": "cdn|static|analytics|api|admin|auth|dynamic|other",
    "priority": 1-10,
    "indicators": ["Liste von erkannten Indikatoren"],
    "pentesting_value": "none|low|medium|high"
}}
"""
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(self.ollama_url, json={
                    "model": "qwen2.5-coder:latest",
                    "prompt": analysis_prompt,
                    "stream": False,
                    "format": "json",
                    "options": {
                        "temperature": 0.2,  # Low temperature for consistent decisions
                        "max_tokens": 500
                    }
                })
                
                if response.status_code == 200:
                    ai_response = response.json()
                    ai_analysis = json.loads(ai_response.get("response", "{}"))
                    
                    # Enhance with additional metadata
                    ai_analysis.update({
                        "url": url,
                        "method": method,
                        "domain": domain,
                        "timestamp": asyncio.get_event_loop().time(),
                        "analysis_type": "ai_powered"
                    })
                    
                    # Update learning data
                    if ai_analysis.get("decision") == "FILTER":
                        self.learning_data["filtered_domains"].append(domain)
                    else:
                        self.learning_data["analyzed_domains"].append(domain)
                    
                    return ai_analysis
                    
        except Exception as e:
            print(f"AI URL analysis failed: {e}")
        
        # Fallback to simple heuristics if AI fails
        return self._fallback_analysis(url, method)
    
    def _fallback_analysis(self, url: str, method: str) -> Dict[str, Any]:
        """Fallback heuristics if AI is not available"""
        
        parsed = urlparse(url.lower())
        domain = parsed.netloc
        path = parsed.path
        
        # Simple heuristic rules
        cdn_indicators = ['cdn', 'static', 'assets', 'googleapis', 'cloudflare', 'jsdelivr']
        static_extensions = ['.js', '.css', '.png', '.jpg', '.gif', '.ico', '.woff']
        api_indicators = ['/api/', '/rest/', '/graphql', '/v1/', '/admin/', '/auth/']
        
        decision = "FILTER"
        category = "other"
        priority = 5
        reasoning = "Heuristic analysis"
        
        # CDN detection
        if any(indicator in domain for indicator in cdn_indicators):
            decision = "FILTER"
            category = "cdn"
            priority = 1
            reasoning = "CDN domain detected"
        
        # Static assets
        elif any(path.endswith(ext) for ext in static_extensions):
            decision = "FILTER"
            category = "static"
            priority = 1
            reasoning = "Static asset detected"
        
        # API endpoints
        elif any(indicator in path for indicator in api_indicators):
            decision = "ANALYZE"
            category = "api"
            priority = 9
            reasoning = "API endpoint detected"
        
        # Non-GET methods
        elif method.upper() in ['POST', 'PUT', 'DELETE', 'PATCH']:
            decision = "ANALYZE"
            category = "dynamic"
            priority = 8
            reasoning = "State-changing HTTP method"
        
        return {
            "decision": decision,
            "confidence": 0.7,
            "reasoning": reasoning,
            "category": category,
            "priority": priority,
            "indicators": ["heuristic_fallback"],
            "pentesting_value": "medium" if decision == "ANALYZE" else "none",
            "url": url,
            "method": method,
            "domain": parsed.netloc,
            "analysis_type": "fallback_heuristic"
        }
    
    def get_filter_stats(self) -> Dict[str, Any]:
        """Get filtering statistics and learning data"""
        
        return {
            "cache_size": len(self.filter_cache),
            "filtered_domains": len(set(self.learning_data["filtered_domains"])),
            "analyzed_domains": len(set(self.learning_data["analyzed_domains"])),
            "total_decisions": len(self.learning_data["filtered_domains"]) + len(self.learning_data["analyzed_domains"]),
            "top_filtered_domains": self._get_top_domains(self.learning_data["filtered_domains"]),
            "top_analyzed_domains": self._get_top_domains(self.learning_data["analyzed_domains"])
        }
    
    def _get_top_domains(self, domain_list: List[str], top_n: int = 10) -> List[Tuple[str, int]]:
        """Get top N most frequent domains"""
        from collections import Counter
        return Counter(domain_list).most_common(top_n)
    
    async def learn_from_feedback(self, url: str, correct_decision: str, reason: str):
        """Learn from user feedback to improve filtering"""
        
        feedback = {
            "url": url,
            "correct_decision": correct_decision,
            "reason": reason,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        self.learning_data["user_feedback"].append(feedback)
        
        # Remove from cache to force re-analysis
        cache_keys_to_remove = [key for key in self.filter_cache.keys() if url in key]
        for key in cache_keys_to_remove:
            del self.filter_cache[key]
