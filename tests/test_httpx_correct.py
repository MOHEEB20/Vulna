"""Test HTTPX transport proxy syntax"""
import asyncio
import httpx

async def test_httpx_proxy():
    print("Testing HTTPX with transport proxy...")
    
    try:
        # Correct HTTPX transport syntax
        transport = httpx.HTTPTransport(proxy="http://localhost:8080")
        
        async with httpx.AsyncClient(transport=transport, timeout=10.0) as client:
            print("Sending request through proxy...")
            response = await client.get("http://httpbin.org/ip")
            
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Success! Data: {data}")
            else:
                print(f"Failed with status: {response.status_code}")
                
    except Exception as e:
        print(f"Error: {e}")
        print("Proxy might not be running on port 8080")

if __name__ == "__main__":
    asyncio.run(test_httpx_proxy())
