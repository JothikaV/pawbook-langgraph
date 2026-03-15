import sys
sys.stdout.reconfigure(encoding='utf-8') if sys.platform == 'win32' else None
import asyncio
import httpx
import json

async def test_single():
    query = "Check availability for tomorrow morning for a dog"
    
    print(f"\nTesting query: {query}\n")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:3100/api/chat",
            json={
                "messages": [{"role": "user", "content": query}],
                "sessionContext": {},
            },
            timeout=30.0
        )
        
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"\nResponse Keys: {data.keys()}")
        print(f"\nFull Response:")
        print(json.dumps(data, indent=2, default=str))

asyncio.run(test_single())
