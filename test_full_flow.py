import sys
sys.stdout.reconfigure(encoding='utf-8') if sys.platform == 'win32' else None
import asyncio
import json
import httpx
from datetime import datetime

# Test queries for the full flow
queries = [
    {
        "step": 1,
        "query": "Check availability for tomorrow morning for a dog",
        "expected_tools": ["check_availability"],
    },
    {
        "step": 2,
        "query": "What's the pricing for a small dog, full grooming service with nail trim and teeth brushing add-ons?",
        "expected_tools": ["get_pricing"],
    },
    {
        "step": 3,
        "query": "I want to book my dog Max (small size) for full grooming tomorrow morning with nail trim and teeth brushing. My name is John Smith, email is john@example.com, phone is 555-1234",
        "expected_tools": ["create_booking"],
    },
    {
        "step": 4,
        "query": "Can you get the details of my booking?",
        "expected_tools": ["get_booking"],
    },
    {
        "step": 5,
        "query": "Send a confirmation notification for my booking",
        "expected_tools": ["send_notification"],
    },
    {
        "step": 6,
        "query": "Get all notifications for my booking",
        "expected_tools": ["get_notifications"],
    },
    {
        "step": 7,
        "query": "Cancel my booking",
        "expected_tools": ["cancel_booking"],
    },
]

async def test_full_flow():
    """Test all 7 queries"""
    print("\n" + "="*80)
    print("🐾 PAWBOOK FULL FLOW TEST - ALL 7 STEPS")
    print("="*80 + "\n")
    
    messages = []
    session_context = {}
    booking_id = None
    results = []
    
    for test_case in queries:
        step = test_case["step"]
        query = test_case["query"]
        expected_tools = test_case["expected_tools"]
        
        print(f"\n{'='*80}")
        print(f"STEP {step}: {query[:60]}...")
        print(f"{'='*80}")
        
        # Add user message
        messages.append({"role": "user", "content": query})
        
        try:
            # Call agent API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://localhost:3100/api/chat",
                    json={
                        "messages": messages,
                        "sessionContext": session_context,
                    },
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    print(f"❌ API ERROR: {response.status_code}")
                    print(f"   {response.text[:200]}")
                    results.append({
                        "step": step,
                        "status": "FAILED",
                        "error": f"HTTP {response.status_code}"
                    })
                    continue
                
                data = response.json()
                
                # Extract response
                message_text = data.get("message", "")
                tools_used = data.get("toolsUsed", [])
                context_updates = data.get("contextUpdates", {})
                graph_meta = data.get("graphMeta", {})
                
                # Add to messages for continuity
                messages.append({"role": "assistant", "content": message_text})
                
                # Update session context
                session_context.update(context_updates)
                
                # Track booking ID for later steps
                if step == 3 and "PB-" in message_text:
                    # Extract booking ID from response
                    import re
                    match = re.search(r'(PB-[A-Z0-9]+)', message_text)
                    if match:
                        booking_id = match.group(1)
                        session_context["lastBookingId"] = booking_id
                
                # Check results
                tools_match = set(tools_used) == set(expected_tools)
                status = "✅ PASS" if tools_match and message_text else "⚠️  WARNING"
                
                print(f"\nQuery: {query}")
                print(f"Status: {status}")
                print(f"Tools Used: {tools_used} (Expected: {expected_tools})")
                print(f"Tools Match: {'✅' if tools_match else '❌'}")
                print(f"Response: {message_text[:150]}...")
                print(f"Context: {context_updates}")
                if booking_id:
                    print(f"Booking ID: {booking_id}")
                
                results.append({
                    "step": step,
                    "status": status,
                    "tools_used": tools_used,
                    "expected_tools": expected_tools,
                    "tools_match": tools_match,
                    "response_length": len(message_text),
                    "context_updates": context_updates,
                })
        
        except Exception as e:
            print(f"❌ EXCEPTION: {str(e)[:100]}")
            results.append({
                "step": step,
                "status": "FAILED",
                "error": str(e)
            })
    
    # Summary
    print("\n\n" + "="*80)
    print("📊 FULL FLOW TEST SUMMARY")
    print("="*80 + "\n")
    
    passed = sum(1 for r in results if "PASS" in r.get("status", ""))
    total = len(results)
    
    print(f"Total Steps: {total}")
    print(f"Passed: {passed}/{total}")
    print(f"Pass Rate: {(passed/total*100):.1f}%\n")
    
    for result in results:
        step = result["step"]
        status = result["status"]
        
        if "FAILED" in result.get("status", ""):
            print(f"Step {step}: {status} - {result.get('error', 'Unknown error')}")
        else:
            tools_match = result.get("tools_match", False)
            tool_status = "✅" if tools_match else "❌"
            print(f"Step {step}: {status} | Tools: {tool_status} {result.get('tools_used')} | Response: {result.get('response_length', 0)} chars")
    
    print("\n" + "="*80)
    
    # Final verdict
    if passed == total:
        print("🎉 ALL TESTS PASSED! Full orchestration working perfectly!")
    elif passed >= total - 1:
        print("⚠️  MOSTLY WORKING - Minor issues detected")
    else:
        print(f"❌ ISSUES DETECTED - {total - passed} test(s) failed")
    
    print("="*80 + "\n")

# Run the test
if __name__ == "__main__":
    asyncio.run(test_full_flow())

