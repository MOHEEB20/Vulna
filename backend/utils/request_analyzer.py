"""Intelligent Request Analysis with Function Calling for Enhanced Filtering"""

import json
import re
from typing import Dict, List, Tuple, Optional
from urllib.parse import urlparse, parse_qs
from backend.utils.url_filter import should_analyze_url, get_analysis_priority, is_likely_api_endpoint


class RequestAnalyzer:
    """Intelligent analyzer for HTTP requests using function calling approach"""
    
    def __init__(self):
        self.analysis_cache = {}
        
    def analyze_request_context(self, method: str, url: str, headers: Dict, body: Optional[str] = None) -> Dict:
        """
        Main analysis function that uses 'function calling' approach to parse requests.
        Returns comprehensive analysis of the request for filtering decisions.
        """
        
        # Generate cache key
        cache_key = f"{method}:{url}:{hash(str(sorted(headers.items())))}"
        if cache_key in self.analysis_cache:
            return self.analysis_cache[cache_key]
        
        analysis = {
            "should_analyze": False,
            "priority_score": 0,
            "analysis_type": "skip",
            "category": "unknown",
            "reasons": [],
            "security_indicators": [],
            "function_calls": []
        }
        
        # Function calling approach - each function analyzes specific aspects
        self._analyze_url_structure(url, method, analysis)
        self._analyze_headers(headers, analysis)
        self._analyze_body_content(body, analysis)
        self._analyze_security_context(method, url, headers, body, analysis)
        self._determine_final_decision(analysis)
        
        # Cache result
        self.analysis_cache[cache_key] = analysis
        return analysis
    
    def _analyze_url_structure(self, url: str, method: str, analysis: Dict) -> None:
        """Function: Analyze URL structure and path patterns"""
        function_call = {
            "function": "analyze_url_structure",
            "parameters": {"url": url, "method": method},
            "results": {}
        }
        
        # Basic URL filtering
        should_analyze = should_analyze_url(url, method)
        priority = get_analysis_priority(url, method)
        
        function_call["results"] = {
            "should_analyze": should_analyze,
            "priority": priority,
            "is_api": is_likely_api_endpoint(url, method)
        }
        
        if not should_analyze:
            analysis["reasons"].append("URL filtered out (CDN/static content)")
            function_call["results"]["filter_reason"] = "static_content_or_cdn"
        else:
            analysis["priority_score"] += priority
            
        analysis["function_calls"].append(function_call)
    
    def _analyze_headers(self, headers: Dict, analysis: Dict) -> None:
        """Function: Analyze HTTP headers for security relevance"""
        function_call = {
            "function": "analyze_headers",
            "parameters": {"header_count": len(headers)},
            "results": {"security_headers": [], "content_type": None, "indicators": []}
        }
        
        content_type = headers.get('content-type', '').lower()
        
        # API Content Types (higher priority)
        if any(api_type in content_type for api_type in ['application/json', 'application/xml', 'application/api']):
            analysis["priority_score"] += 2
            analysis["security_indicators"].append("API content type")
            function_call["results"]["indicators"].append("api_content_type")
        
        # Form data (medium priority)
        if 'application/x-www-form-urlencoded' in content_type or 'multipart/form-data' in content_type:
            analysis["priority_score"] += 1
            analysis["security_indicators"].append("Form submission")
            function_call["results"]["indicators"].append("form_submission")
        
        # Authentication headers
        auth_headers = ['authorization', 'x-auth-token', 'x-api-key', 'cookie']
        for header in auth_headers:
            if header in [h.lower() for h in headers.keys()]:
                analysis["priority_score"] += 1
                analysis["security_indicators"].append(f"Authentication header: {header}")
                function_call["results"]["security_headers"].append(header)
        
        function_call["results"]["content_type"] = content_type
        analysis["function_calls"].append(function_call)
    
    def _analyze_body_content(self, body: Optional[str], analysis: Dict) -> None:
        """Function: Analyze request body for security-relevant content"""
        function_call = {
            "function": "analyze_body_content",
            "parameters": {"has_body": body is not None, "body_length": len(body) if body else 0},
            "results": {"body_type": None, "security_parameters": [], "indicators": []}
        }
        
        if not body:
            analysis["function_calls"].append(function_call)
            return
        
        try:
            # JSON body analysis
            if body.strip().startswith('{') or body.strip().startswith('['):
                json_data = json.loads(body)
                analysis["priority_score"] += 2
                analysis["security_indicators"].append("JSON API request")
                function_call["results"]["body_type"] = "json"
                function_call["results"]["indicators"].append("json_api")
                
                # Look for sensitive parameters in JSON
                sensitive_params = self._find_sensitive_parameters(str(json_data))
                if sensitive_params:
                    analysis["priority_score"] += 1
                    function_call["results"]["security_parameters"] = sensitive_params
            
            # Form data analysis
            elif '=' in body:
                analysis["priority_score"] += 1
                analysis["security_indicators"].append("Form data submission")
                function_call["results"]["body_type"] = "form"
                
                # Parse form parameters
                form_params = parse_qs(body)
                sensitive_params = self._find_sensitive_parameters(str(form_params))
                if sensitive_params:
                    analysis["priority_score"] += 1
                    function_call["results"]["security_parameters"] = sensitive_params
        
        except (json.JSONDecodeError, Exception):
            # Raw body content
            analysis["security_indicators"].append("Raw body content")
            function_call["results"]["body_type"] = "raw"
        
        analysis["function_calls"].append(function_call)
    
    def _analyze_security_context(self, method: str, url: str, headers: Dict, body: Optional[str], analysis: Dict) -> None:
        """Function: High-level security context analysis"""
        function_call = {
            "function": "analyze_security_context",
            "parameters": {"method": method, "url": url},
            "results": {"context_type": None, "risk_indicators": [], "recommendations": []}
        }
        
        parsed = urlparse(url.lower())
        path = parsed.path
        
        # High-risk contexts
        high_risk_contexts = {
            '/admin': 'administrative_panel',
            '/login': 'authentication',
            '/upload': 'file_upload',
            '/api/': 'api_endpoint',
            '/config': 'configuration',
            '/debug': 'debug_endpoint'
        }
        
        for risk_path, context in high_risk_contexts.items():
            if risk_path in path:
                analysis["priority_score"] += 3
                analysis["category"] = context
                function_call["results"]["context_type"] = context
                function_call["results"]["risk_indicators"].append(f"High-risk path: {risk_path}")
                break
        
        # Method-based risk assessment
        if method.upper() in ['POST', 'PUT', 'DELETE', 'PATCH']:
            analysis["priority_score"] += 2
            function_call["results"]["risk_indicators"].append(f"State-changing method: {method}")
        
        # Parameter injection opportunities
        if '?' in url or (body and ('=' in body or '{' in body)):
            analysis["priority_score"] += 1
            function_call["results"]["risk_indicators"].append("Parameter injection opportunity")
        
        analysis["function_calls"].append(function_call)
    
    def _find_sensitive_parameters(self, content: str) -> List[str]:
        """Find potentially sensitive parameters in content"""
        sensitive_patterns = [
            r'password', r'passwd', r'pwd', r'secret', r'token', r'key',
            r'user', r'username', r'email', r'id', r'session', r'auth',
            r'sql', r'query', r'command', r'exec', r'file', r'path'
        ]
        
        found_params = []
        content_lower = content.lower()
        
        for pattern in sensitive_patterns:
            if re.search(pattern, content_lower):
                found_params.append(pattern)
        
        return found_params
    
    def _determine_final_decision(self, analysis: Dict) -> None:
        """Function: Make final analysis decision based on all factors"""
        function_call = {
            "function": "determine_final_decision",
            "parameters": {"priority_score": analysis["priority_score"]},
            "results": {"decision": None, "reasoning": []}
        }
        
        priority_score = analysis["priority_score"]
        
        # Decision thresholds
        if priority_score >= 8:
            analysis["should_analyze"] = True
            analysis["analysis_type"] = "ai_deep_analysis"
            function_call["results"]["decision"] = "ai_deep_analysis"
            function_call["results"]["reasoning"].append("High priority score - requires AI analysis")
            
        elif priority_score >= 5:
            analysis["should_analyze"] = True
            analysis["analysis_type"] = "ai_standard_analysis"
            function_call["results"]["decision"] = "ai_standard_analysis"
            function_call["results"]["reasoning"].append("Medium priority - standard AI analysis")
            
        elif priority_score >= 3:
            analysis["should_analyze"] = True
            analysis["analysis_type"] = "pattern_matching"
            function_call["results"]["decision"] = "pattern_matching"
            function_call["results"]["reasoning"].append("Low priority - pattern matching only")
            
        else:
            analysis["should_analyze"] = False
            analysis["analysis_type"] = "skip"
            function_call["results"]["decision"] = "skip"
            function_call["results"]["reasoning"].append("Too low priority - skip analysis")
        
        # Override for filtered URLs
        if any("filtered out" in reason for reason in analysis["reasons"]):
            analysis["should_analyze"] = False
            analysis["analysis_type"] = "skip"
            function_call["results"]["decision"] = "skip"
            function_call["results"]["reasoning"].append("URL filtered by static content rules")
        
        analysis["function_calls"].append(function_call)
    
    def get_analysis_summary(self, analysis: Dict) -> str:
        """Generate human-readable summary of analysis"""
        summary_parts = [
            f"Decision: {analysis['analysis_type']}",
            f"Priority: {analysis['priority_score']}/10",
            f"Category: {analysis.get('category', 'unknown')}"
        ]
        
        if analysis["security_indicators"]:
            summary_parts.append(f"Indicators: {', '.join(analysis['security_indicators'])}")
        
        if analysis["reasons"]:
            summary_parts.append(f"Reasons: {', '.join(analysis['reasons'])}")
        
        return " | ".join(summary_parts)
