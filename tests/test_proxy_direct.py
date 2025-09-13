"""Test proxy directly without Chrome browser"""

import asyncio
import httpx

async def test_proxy():
    """Direct proxy test"""
    print("Testing proxy directly...")
    
    proxy_port = 8080
    
    try:
        # Test with httpx (correct syntax)
        async with httpx.AsyncClient(
            proxies=f"http://localhost:{proxy_port}",
            timeout=10.0
        ) as client:
            print(f"Sending request through proxy localhost:{proxy_port}")
            response = await client.get("http://httpbin.org/ip")
            
            print(f"Response status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Response data: {data}")
                print("✅ PROXY WORKS!")
            else:
                print("❌ Proxy returned non-200 status")
                
    except Exception as e:
        print(f"❌ Proxy test failed: {e}")
        print("   Possible issues:")
        print("   - mitmproxy not running on port 8080")
        print("   - mitmproxy certificate issues") 
        print("   - Firewall blocking connection")

if __name__ == "__main__":
    asyncio.run(test_proxy())
