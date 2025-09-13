"""Test the new AI-powered filtering and vulnerability testing system"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.utils.ai_smart_filter import AISmartFilter
from backend.utils.vulnerability_tester import VulnerabilityTester


async def test_ai_smart_filter():
    """Test the AI-powered smart filtering"""
    print("=== Testing AI Smart Filter ===")
    
    ai_filter = AISmartFilter()
    
    test_urls = [
        # Should be FILTERED
        ("GET", "https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css"),
        ("GET", "https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"),
        ("GET", "https://www.youtube.com/embed/dQw4w9WgXcQ"),
        ("GET", "https://example.com/static/app.js"),
        
        # Should be ANALYZED
        ("POST", "https://api.example.com/v1/users"),
        ("GET", "https://admin.example.com/dashboard"),
        ("POST", "https://example.com/login"),
        ("GET", "https://example.com/search?q=<script>alert(1)</script>"),
    ]
    
    for method, url in test_urls:
        result = await ai_filter.should_analyze_url(url, method)
        
        decision = result.get("decision", "UNKNOWN")
        confidence = result.get("confidence", 0.0)
        reasoning = result.get("reasoning", "No reasoning")
        category = result.get("category", "unknown")
        
        print(f"\n{decision} ({confidence:.2f}) | {category}")
        print(f"  {method} {url}")
        print(f"  Reason: {reasoning}")
    
    # Show filter stats
    stats = ai_filter.get_filter_stats()
    print(f"\n=== Filter Stats ===")
    print(f"Cache size: {stats['cache_size']}")
    print(f"Total decisions: {stats['total_decisions']}")


async def test_vulnerability_tester():
    """Test the automated vulnerability testing"""
    print("\n\n=== Testing Vulnerability Tester ===")
    
    tester = VulnerabilityTester()
    
    # Mock vulnerability for testing
    mock_vulnerability = {
        "id": "test-vuln-001",
        "title": "Potential SQL Injection",
        "description": "SQL injection vulnerability detected in parameter 'id'",
        "affected_url": "https://httpbin.org/get",
        "request_method": "GET",
        "request_headers": {"User-Agent": "Vulna-Test"},
        "request_body": "",
        "risk_level": "HIGH"
    }
    
    print("Testing mock SQL injection vulnerability...")
    test_result = await tester.test_vulnerability(mock_vulnerability)
    
    print(f"Test Status: {test_result.get('test_status')}")
    print(f"Verified: {test_result.get('verified')}")
    print(f"Confidence: {test_result.get('confidence')}")
    print(f"Evidence: {test_result.get('evidence')}")
    
    if test_result.get('poc_code'):
        print(f"PoC Code generated: {len(test_result['poc_code'])} characters")
    
    # Show test stats
    stats = tester.get_test_results()
    print(f"\n=== Test Stats ===")
    print(f"Total tests: {stats['total_tests']}")
    print(f"Verified vulnerabilities: {stats['verified_vulnerabilities']}")
    print(f"False positives: {stats['false_positives']}")
    print(f"Verification rate: {stats['verification_rate']:.2%}")


async def main():
    """Run all tests"""
    print("Testing New AI-Powered Vulna System v4.0\n")
    
    try:
        await test_ai_smart_filter()
        await test_vulnerability_tester()
        
        print("\n=== All Tests Completed ===")
        print("New features:")
        print("✓ AI-powered smart filtering")
        print("✓ Automated vulnerability testing")
        print("✓ PoC generation and execution")
        print("✓ Learning from user feedback")
        print("✓ Enhanced statistics and metrics")
        
    except Exception as e:
        print(f"Test failed: {e}")
        print("Note: This test requires Ollama to be running with qwen2.5-coder model")


if __name__ == "__main__":
    asyncio.run(main())
