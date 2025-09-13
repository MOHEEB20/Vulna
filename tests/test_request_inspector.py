#!/usr/bin/env python3
"""
Test script for Request Inspector functionality
"""

import requests
import json
import time

def test_request_inspector():
    """Test the request inspector API endpoints"""
    base_url = "http://localhost:3000"
    
    print("🧪 Testing Request Inspector System")
    print("=" * 50)
    
    # Test data
    test_request = {
        "method": "POST",
        "url": "https://httpbin.org/post",
        "headers": {
            "Content-Type": "application/json",
            "User-Agent": "Vulna-Test/1.0"
        },
        "body": json.dumps({
            "test_param": "test_value",
            "xss_test": "<script>alert('test')</script>"
        })
    }
    
    # Test 1: Test Request Endpoint
    print("\n1. Testing /api/test-request endpoint...")
    try:
        response = requests.post(
            f"{base_url}/api/test-request",
            json=test_request,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ Request test successful")
                print(f"   Status: {data.get('status_code')}")
                print(f"   Response time: {data.get('response_time')}ms")
                print(f"   Response length: {len(data.get('response_body', ''))}")
            else:
                print(f"❌ Request test failed: {data.get('message')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 2: Test Vulnerability Analysis
    print("\n2. Testing /api/test-request-vulnerabilities endpoint...")
    try:
        response = requests.post(
            f"{base_url}/api/test-request-vulnerabilities",
            json=test_request,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ Vulnerability analysis successful")
                analysis = data.get('analysis', '')
                print(f"   Analysis length: {len(analysis)} characters")
                if 'INJECTION' in analysis.upper():
                    print("   ✅ Contains injection analysis")
                if 'XSS' in analysis.upper():
                    print("   ✅ Contains XSS analysis")
            else:
                print(f"❌ Vulnerability analysis failed: {data.get('message')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 3: Frontend Integration Test
    print("\n3. Testing Frontend Integration...")
    test_cases = [
        {
            "name": "XSS Request",
            "request": {
                "method": "GET",
                "url": "https://example.com/search?q=<script>alert(1)</script>",
                "headers": {"User-Agent": "Test"},
                "body": ""
            }
        },
        {
            "name": "SQL Injection Request", 
            "request": {
                "method": "POST",
                "url": "https://example.com/login",
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"username": "admin' OR '1'='1", "password": "test"})
            }
        }
    ]
    
    for case in test_cases:
        print(f"\n   Testing {case['name']}...")
        try:
            response = requests.post(
                f"{base_url}/api/test-request-vulnerabilities",
                json=case["request"],
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    analysis = data.get('analysis', '').upper()
                    if 'INJECTION' in analysis or 'XSS' in analysis or 'VULNERABILITY' in analysis:
                        print(f"   ✅ {case['name']} detected in analysis")
                    else:
                        print(f"   ⚠️  {case['name']} may not be detected")
                else:
                    print(f"   ❌ Analysis failed: {data.get('message')}")
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Request Inspector Test Complete!")
    print("\n🎯 Next Steps:")
    print("1. Start Vulna dashboard: python -m backend.main")
    print("2. Open browser: http://localhost:3000")
    print("3. Click on any request → 'Send to Inspector'")
    print("4. Test tamper functionality with payloads")
    print("5. Use 'Test Request' to verify modifications")

if __name__ == "__main__":
    test_request_inspector()
