"""Test HTTPX correct proxy syntax"""
import asyncio
import httpx

async def test_httpx_correct():
    print("Testing HTTPX with CORRECT proxy syntax...")
    
    try:
        # CORRECT HTTPX proxy syntax for httpx 0.28+
        async with httpx.AsyncClient(
            proxies={"http://": "http://localhost:8080", "https://": "http://localhost:8080"},
            timeout=10.0
        ) as client:
            print("Sending request through proxy...")
            response = await client.get("http://httpbin.org/ip")
            
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"SUCCESS! Data: {data}")
                print("✅ PROXY WORKS!")
            else:
                print(f"Failed with status: {response.status_code}")
                
    except Exception as e:
        print(f"Error: {e}")
        print("Proxy might not be running or configured correctly")

if __name__ == "__main__":
    asyncio.run(test_httpx_correct())
