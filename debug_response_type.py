import sys
sys.stdout.reconfigure(encoding='utf-8') if sys.platform == 'win32' else None
import asyncio
import httpx

async def test():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:3100/api/chat",
            json={
                "messages": [{"role": "user", "content": "Check availability for tomorrow for a dog"}],
                "sessionContext": {},
            },
        )
        
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        print(f"Raw response type: {type(response.json())}")
        print(f"Raw response (first 500 chars): {str(response.content[:500])}")
        
        data = response.json()
        if isinstance(data, list):
            print(f"\nERROR: Response is a LIST with {len(data)} items!")
            print(f"First item type: {type(data[0])}")
            if data:
                print(f"First item: {str(data[0])[:200]}")
        else:
            print(f"Response is a dict with keys: {data.keys()}")

asyncio.run(test())
