"""Test script for enhanced filtering system"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.utils.url_filter import should_analyze_url, get_analysis_priority, categorize_url
from backend.utils.request_analyzer import RequestAnalyzer

def test_url_filtering():
    """Test URL filtering functionality"""
    print("Testing URL Filtering System\n")
    
    test_urls = [
        # Should be FILTERED (CDN/Static)
        ("GET", "https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"),
        ("GET", "https://fonts.googleapis.com/css?family=Roboto"),
        ("GET", "https://www.google-analytics.com/analytics.js"),
        ("GET", "https://example.com/static/app.js"),
        ("GET", "https://example.com/images/logo.png"),
        
        # Should be ANALYZED (API/Dynamic)
        ("POST", "https://api.example.com/v1/users"),
        ("GET", "https://example.com/api/search?q=test"),
        ("PUT", "https://example.com/admin/users/123"),
        ("POST", "https://example.com/login"),
        ("GET", "https://example.com/profile?id=123"),
        
        # Medium priority
        ("GET", "https://example.com/search?query=test"),
        ("POST", "https://example.com/upload"),
        ("GET", "https://example.com/admin/dashboard"),
    ]
    
    analyzer = RequestAnalyzer()
    
    for method, url in test_urls:
        should_analyze = should_analyze_url(url, method)
        priority = get_analysis_priority(url, method)
        category = categorize_url(url, method)
        
        # Test function calling analyzer
        analysis = analyzer.analyze_request_context(
            method=method,
            url=url,
            headers={"content-type": "application/json", "user-agent": "test"},
            body='{"test": "data"}' if method in ["POST", "PUT"] else None
        )
        
        status = "ANALYZE" if should_analyze else "FILTER"
        print(f"{status} | P{priority}/10 | {category}")
        print(f"   {method} {url}")
        print(f"   Analysis: {analysis['analysis_type']} (Score: {analysis['priority_score']})")
        
        if analysis["security_indicators"]:
            print(f"   Indicators: {', '.join(analysis['security_indicators'])}")
        
        print()

def test_function_calling_analysis():
    """Test function calling analysis system"""
    print("\nTesting Function Calling Analysis\n")
    
    test_cases = [
        {
            "name": "High Priority API Request",
            "method": "POST",
            "url": "https://api.example.com/v1/admin/users",
            "headers": {"content-type": "application/json", "authorization": "Bearer token"},
            "body": '{"username": "admin", "password": "secret123"}'
        },
        {
            "name": "Medium Priority Search",
            "method": "GET", 
            "url": "https://example.com/search?q=<script>alert(1)</script>",
            "headers": {"user-agent": "Mozilla/5.0"},
            "body": None
        },
        {
            "name": "Low Priority Static Request",
            "method": "GET",
            "url": "https://example.com/about.html",
            "headers": {"user-agent": "Mozilla/5.0"},
            "body": None
        }
    ]
    
    analyzer = RequestAnalyzer()
    
    for case in test_cases:
        print(f"Case: {case['name']}")
        print(f"   {case['method']} {case['url']}")
        
        analysis = analyzer.analyze_request_context(
            method=case["method"],
            url=case["url"],
            headers=case["headers"],
            body=case["body"]
        )
        
        print(f"   Decision: {analysis['analysis_type']}")
        print(f"   Priority Score: {analysis['priority_score']}/10")
        print(f"   Should Analyze: {analysis['should_analyze']}")
        
        if analysis["security_indicators"]:
            print(f"   Security Indicators: {', '.join(analysis['security_indicators'])}")
        
        if analysis["function_calls"]:
            print(f"   Function Calls: {len(analysis['function_calls'])}")
            for fc in analysis["function_calls"]:
                print(f"     - {fc['function']}: {fc['results']}")
        
        print()

if __name__ == "__main__":
    test_url_filtering()
    test_function_calling_analysis()
    print("All tests completed!")
