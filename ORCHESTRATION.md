# 🐾 PawBook Orchestration - Complete System Guide

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     React Frontend (Port 3001)                          │
│              Chat Interface with Real-time Status Updates               │
└──────────────────────────┬──────────────────────────────────────────────┘
                           │ HTTP REST API (POST /api/chat)
                           ↓
┌──────────────────────────────────────────────────────────────────────┐
│                   Agent Orchestration Layer                          │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  Groq LLM (Free Tier)                                      │    │
│  │  • Natural language understanding                           │    │
│  │  • Tool decision making                                     │    │
│  │  • Response generation                                      │    │
│  └─────────────────────────────────────────────────────────────┘    │
│  Port: 3100                                                          │
│  Framework: FastAPI (async Python)                                   │
│  Agent Type: PawBookGraph (LangGraph StateGraph)                    │
└──────────┬───────────────────────────────────────────────────────────┘
           │ JSON-RPC 2.0 over HTTP (Sync httpx client)
           │
    ┌──────┴──────────────┬───────────────┬──────────────┐
    ↓                     ↓               ↓              ↓
┌─────────┐            ┌──────────┐    ┌────────┐    ┌──────────┐
│Availability        │Pricing   │    │Booking │    │Notification
│Server              │Server    │    │Server  │    │Server
│Port 3101           │Port 3102 │    │Port 3103   │Port 3104
│2 Tools             │2 Tools   │    │3 Tools │    │2 Tools
└─────────┘            └──────────┘    └────────┘    └──────────┘
```

## Agent Orchestration Implementation

### 1. LangGraph StateGraph Architecture

The system uses **one PawBookGraph** powered by LangGraph StateGraph.

```
START
  ↓
┌────────────────────────────────┐
│   agent_node()                 │
│  • Call LLM with bind_tools()  │
│  • Extract context (petType)   │
│  • Return response             │
└──────────┬─────────────────────┘
           ↓
┌────────────────────────────────┐
│ should_continue()              │
│ Check: tool_calls in message?  │
└──┬────────────────────────┬────┘
   │                        │
YES │                        │ NO
   ↓                        ↓
┌─────────────────┐    ┌──────────┐
│ ToolNode        │    │   END    │
│ • Execute tools │    └──────────┘
│ • Create msgs   │
└─────┬───────────┘
      │
      └──→ [Loop back to agent_node]
```

### 2. GraphState Type Definition

```python
class GraphState(TypedDict):
    # Messages with LangChain's add_messages reducer
    messages: Annotated[list[BaseMessage], add_messages]

    # Session context with custom merge_dicts reducer
    sessionContext: Annotated[dict, merge_dicts]

    # Tool call log with list concatenation
    toolCallLog: Annotated[list, operator.add]
```

**Reducers:**
- `add_messages` - Appends new messages, deduplicates by ID
- `merge_dicts` - Updates context dict (old + new)
- `operator.add` - Concatenates tool call log entries

### 3. Agent Decision Tree

When LLM receives a user query, it decides which tools to call:

```
User Query
    ↓
Does mention AVAILABILITY/SLOTS/GROOMERS?
    ├─ YES → call check_availability or list_groomers
    ├─ NO → continue
    ↓
Does mention PRICING/COST/PRICE?
    ├─ YES → call get_pricing or list_addons
    ├─ NO → continue
    ↓
Does mention BOOK/APPOINTMENT/SCHEDULE?
    ├─ YES → call create_booking (after confirming slot/pricing)
    ├─ NO → continue
    ↓
Does mention BOOKING DETAILS/CONFIRMATION?
    ├─ YES → call get_booking
    ├─ NO → continue
    ↓
Does mention CANCEL/CANCELLATION?
    ├─ YES → call cancel_booking
    ├─ NO → continue
    ↓
Does mention NOTIFICATION/REMINDER?
    ├─ YES → call send_notification or get_notifications
    ├─ NO → continue
    ↓
Respond conversationally without tools
```

### 4. Session Context Tracking

Agent maintains state across conversation turns:

```
Turn 1: "Check availability for a dog tomorrow"
  Context: {petType: "dog"}

Turn 2: "Book Max for 10:30 AM"
  Context: {petType: "dog", petName: "Max"}

Turn 3: "Send confirmation"
  Context: {petType: "dog", petName: "Max", lastBookingId: "PB-ABC123"}
```

**Context Updates:**
- `check_availability()` → extract `petType`
- `get_pricing()` → extract `petSize`, `service`, `selectedAddOns`
- `create_booking()` → extract `petName`, `lastBookingId`
- Persist across conversation turns

## Example Conversation Flows

### Flow 1: Check Availability

```
User: "Check availability for tomorrow morning for a dog"
      ↓
[Agent] LLM reads: "availability" + "tomorrow" + "morning" + "dog"
      ↓
[LLM Decision] "Use check_availability tool"
      ↓
[Tool Call]
  Method: tools/call
  Params: {
    name: "check_availability",
    arguments: {
      date: "tomorrow",
      timePreference: "morning",
      petType: "dog"
    }
  }
      ↓
[MCP Server :3101 Response]
  {
    "slots": [
      {
        "slotId": "slot-001",
        "date": "2026-03-16",
        "time": "9:00 AM",
        "groomerName": "Sarah Chen",
        "groomerRating": 4.9
      },
      {
        "slotId": "slot-002",
        "time": "10:30 AM",
        "groomerName": "Marcus Rivera",
        "groomerRating": 4.8
      },
      ...
    ]
  }
      ↓
[ToolMessage Created] Result appended to messages
      ↓
[Agent 2nd Pass] LLM reads results and generates response:
  "I found 3 available slots tomorrow morning for your dog:
   1. 9:00 AM with Sarah Chen (4.9★)
   2. 10:30 AM with Marcus Rivera (4.8★)
   3. 12:00 PM with Priya Nair (4.7★)"
      ↓
[Response] Sent to frontend with tool badges
```

### Flow 2: Complete Booking Flow (Multi-Step)

```
User: "Book my dog Max (small) for full grooming tomorrow morning
       with nail trim and teeth brushing. I'm John Smith,
       john@example.com, 555-1234"
      ↓
[Step 1: Check Availability]
  Tool: check_availability
  Args: {date: "tomorrow", timePreference: "morning", petType: "dog"}
  Result: slot-id-123 found
      ↓
[Step 2: Get Pricing]
  Tool: get_pricing
  Args: {
    petType: "dog",
    petSize: "small",
    serviceType: "full",
    selectedAddOns: ["nail_trim", "teeth_brushing"]
  }
  Result: {
    basePrice: 60,
    addOns: [{name: "nail_trim", price: 10}, {name: "teeth_brushing", price: 12}],
    totalPrice: 82
  }
      ↓
[Step 3: Create Booking]
  Tool: create_booking
  Args: {
    slotId: "slot-id-123",
    petName: "Max",
    petType: "dog",
    petSize: "small",
    serviceType: "full",
    customerName: "John Smith",
    customerEmail: "john@example.com",
    customerPhone: "555-1234",
    selectedAddOns: ["nail_trim", "teeth_brushing"]
  }
  Result: {
    bookingId: "PB-ABC123",
    status: "confirmed",
    totalPrice: 82
  }
      ↓
[Step 4: Send Notification]
  Tool: send_notification
  Args: {
    bookingId: "PB-ABC123",
    type: "confirmation",
    channels: ["email", "sms"]
  }
  Result: {
    notifId: "NOTIF-XYZ",
    status: "delivered"
  }
      ↓
[Agent Response]
  "✅ Booking confirmed!
   Appointment ID: PB-ABC123
   Pet: Max (small dog)
   Service: Full grooming with nail trim & teeth brushing ($82)
   Date: Tomorrow at 9:00 AM with Sarah Chen
   Confirmation sent to john@example.com"
      ↓
[Frontend Display]
  Message with badges: [check_availability] [get_pricing]
                       [create_booking] [send_notification]
```

### Flow 3: Query with Pricing

```
User: "How much for a large cat full grooming with nail trim
       and teeth brushing?"
      ↓
[Tool Call] get_pricing
  Args: {
    petType: "cat",
    petSize: "large",
    serviceType: "full",
    selectedAddOns: ["nail_trim", "teeth_brushing"]
  }
      ↓
[MCP Response]
  {
    "basePrice": 85,
    "addOns": [
      {"name": "nail_trim", "price": 10},
      {"name": "teeth_brushing", "price": 12}
    ],
    "totalPrice": 107
  }
      ↓
[Agent Response]
  "For a large cat with full grooming:
   • Base price: $85
   • Nail trim: +$10
   • Teeth brushing: +$12
   • Total: $107"
      ↓
[Frontend]
  Message with badge: [get_pricing]
```

## Tool Ecosystem (9 Total Tools)

### Tool Distribution by Server

#### 1. Availability Server (Port 3101) - 2 Tools

| Tool | Purpose | Input | Returns |
|------|---------|-------|---------|
| `check_availability` | Find available slots | date, timePreference, petType | slots with groomer info |
| `list_groomers` | Show all groomers | - | 4 groomers with ratings |

**Data:**
- 4 Groomers: Sarah Chen (4.9★), Marcus Rivera (4.8★), Priya Nair (4.7★), Tom Walsh (4.6★)
- 70+ Slots per week (7 days × 5 times × 4 groomers with 70% probability)
- Specializations: Dogs, cats, rabbits

#### 2. Pricing Server (Port 3102) - 2 Tools

| Tool | Purpose | Input | Returns |
|------|---------|-------|---------|
| `get_pricing` | Calculate cost | petType, petSize, service, addOns | price breakdown |
| `list_addons` | Show add-ons | - | 5 add-on services |

**Pricing Matrix:**
- Pet Types: dog, cat, rabbit
- Sizes: small, medium, large, giant
- Services: basic, full, bath_only
- Add-ons: nail_trim ($10), teeth_brushing ($12), flea_treatment ($20), bow_accessory ($5), paw_balm ($8)

**Example:** Small dog full grooming = $60 base

#### 3. Booking Server (Port 3103) - 3 Tools

| Tool | Purpose | Input | Returns |
|------|---------|-------|---------|
| `create_booking` | Create appointment | slotId, petName, customer details, service | bookingId, confirmation |
| `get_booking` | Retrieve booking | bookingId | full booking object |
| `cancel_booking` | Cancel appointment | bookingId | cancellation confirmation |

**Workflow:**
1. Validate slot availability
2. Generate booking ID: `PB-XXXXXXXX`
3. Mark slot as booked
4. Calculate pricing
5. Store booking
6. Return confirmation

#### 4. Notification Server (Port 3104) - 2 Tools

| Tool | Purpose | Input | Returns |
|------|---------|-------|---------|
| `send_notification` | Send message | bookingId, type, channels | notification status |
| `get_notifications` | Retrieve messages | bookingId | all notifications |

**Channels:** Email, SMS, Push (mocked)
**Types:** confirmation, reminder

## MCP Protocol Implementation

### JSON-RPC 2.0 Flow

```
Client Request (Agent Server):
  POST http://localhost:3101/mcp
  {
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "check_availability",
      "arguments": {
        "date": "tomorrow",
        "timePreference": "morning",
        "petType": "dog"
      }
    },
    "id": "1"
  }
      ↓
Server Processing (MCP Server):
  1. Parse request
  2. Find tool handler
  3. Execute function
  4. Format result
      ↓
Server Response:
  {
    "jsonrpc": "2.0",
    "result": {
      "content": [{
        "type": "text",
        "text": "{...JSON result...}"
      }],
      "isError": false
    },
    "id": "1"
  }
      ↓
Client Processing:
  1. Extract content[0].text
  2. Parse JSON
  3. Return to tool wrapper
  4. Create ToolMessage
  5. Append to state
```

### Tool Discovery

```
Agent Startup
    ↓
For each MCP Server (3101, 3102, 3103, 3104):
    1. Send: {method: "initialize"}
    2. Receive: {name: "pawbook-*", version: "1.0.0"}
    3. Send: {method: "tools/list"}
    4. Receive: [{name: "tool1", description: "...", inputSchema: {...}}, ...]
    5. Create Pydantic model from JSON schema
    6. Create LangChain StructuredTool wrapper
    7. Store tool in tools dict
    ↓
Agent ready with 9 tools
```

## Performance Characteristics

### Latency Breakdown (per request)

```
User Query
    ↓ 50ms (network)
[Agent] LLM Call
    ↓ 1.5s (Groq inference)
[Tool Execution] (if tools called)
    ↓ 300ms (HTTP to MCP server)
[Agent] LLM Response Generation
    ↓ 1.5s (Groq inference)
[Response] Sent to Frontend
    ↓ 50ms (network)

Total: ~3.3 seconds per request
```

### Throughput
- Requests: Sequential (1 agent at a time)
- Tools: Can be called 2-4 per request
- Rate Limit: Dependent on LLM provider
  - Groq free: 100,000 tokens/day
  - ~10-20 requests per minute on free tier

## Session Context Example

### Multi-Turn Conversation

```
Turn 1: User: "Check availability for a dog tomorrow morning"
  Context: {petType: "dog"}
  Messages: [HumanMessage, AIMessage, ToolMessage, AIMessage]
      ↓
Turn 2: User: "Book Max for 10:30 AM"
  Context: {petType: "dog", petName: "Max", lastBookingId: "PB-ABC123"}
  Messages: [...previous messages..., HumanMessage, AIMessage, ToolMessage, AIMessage]
      ↓
Turn 3: User: "Send confirmation"
  Context: {petType: "dog", petName: "Max", lastBookingId: "PB-ABC123"}
  Messages: [...all previous messages..., HumanMessage, AIMessage]
```

**Key Benefit:** Context persists! Agent remembers petType, petName, bookingId across turns.

## Testing the Full Flow

### 7-Step Test Sequence

```
1. Check availability for tomorrow morning for a dog
   → Tools: check_availability
   → Result: 3-6 available slots

2. What's the pricing for a small dog, full grooming with nail trim + teeth brushing?
   → Tools: get_pricing
   → Result: $82 ($60 base + $10 + $12)

3. Book my dog Max for full grooming tomorrow...
   → Tools: check_availability, create_booking, send_notification
   → Result: Booking ID PB-ABC123 confirmed

4. Get my booking details
   → Tools: get_booking
   → Result: Full booking object

5. Send confirmation notification
   → Tools: send_notification
   → Result: Notification sent

6. Get all my notifications
   → Tools: get_notifications
   → Result: List of all notifications

7. Cancel my booking
   → Tools: cancel_booking
   → Result: Booking cancelled, slot freed
```

## Summary Table

| Aspect | Details |
|--------|---------|
| **Agents** | 1 (PawBookGraph - LangGraph StateGraph) |
| **MCP Servers** | 4 (availability, pricing, booking, notification) |
| **Tools** | 9 total |
| **Groomers** | 4 (Sarah, Marcus, Priya, Tom) |
| **Services** | 3 (basic, full, bath_only) |
| **Add-ons** | 5 |
| **Max Slots/Day** | 70+ |
| **LLM** | Groq API (Free Tier) |
| **Protocol** | JSON-RPC 2.0 / HTTP POST |
| **Latency** | ~3.3 seconds per request |
| **Concurrency** | Sequential (1 agent) |

## Key Features

✅ Professional LangGraph StateGraph architecture
✅ Clear node and edge definitions
✅ Explicit state management with TypedDict
✅ Reducer functions for state updates
✅ Automatic tool execution with ToolNode
✅ Conditional routing with should_continue
✅ Multi-turn conversation with context preservation
✅ Type-safe state handling
✅ Comprehensive logging at each node
✅ 100% backwards compatible with frontend
✅ Production-ready implementation

---

**Framework**: LangGraph + LangChain + MCP
**Status**: ✅ Production Ready
**Last Updated**: March 15, 2026
