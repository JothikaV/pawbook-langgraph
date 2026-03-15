"""
agent/graph.py
LangGraph-based agent orchestration with StateGraph.
"""
import os
import json
import operator
from typing import Any, Annotated, TypedDict
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    AIMessage,
    SystemMessage,
    ToolMessage,
)
from langgraph.graph.message import add_messages
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from shared.logger import setup_logger

logger = setup_logger("LangGraphAgent")


SYSTEM_PROMPT = """You are PawBook, a friendly pet grooming assistant. Help customers book grooming appointments.

Available services: basic, full, bath_only
Pet types: dog, cat, rabbit
Sizes: small, medium, large, giant
Add-ons: nail_trim, teeth_brushing, flea_treatment, bow_accessory, paw_balm

IMPORTANT WORKFLOW:
1. AVAILABILITY: If user asks about availability → call check_availability with date (today/tomorrow/YYYY-MM-DD), timePreference (morning/afternoon/evening/any), and petType
2. PRICING: If user asks about cost → call get_pricing with petType, petSize, serviceType, and selectedAddOns (list of addon IDs like ["nail_trim", "teeth_brushing"])
3. BOOKING: If user wants to book:
   - First call check_availability if you don't have available slots already
   - Then call create_booking with ONLY these required fields (do NOT include groomerId):
     * slotId: The exact slotId from check_availability results (e.g. "slot-2026-03-16-g1-28")
     * petName: Name of the pet
     * petType: dog/cat/rabbit
     * petSize: small/medium/large/giant
     * serviceType: basic/full/bath_only
     * customerName: Full name
     * customerEmail: Email address
     * customerPhone: Phone number
     * selectedAddOns: List of addon IDs (e.g. ["nail_trim"] or [] if no add-ons)
4. GET BOOKING: If user asks for booking details → use get_booking with booking ID
5. SEND NOTIFICATION: If user wants confirmation/reminder sent → use send_notification with bookingId
6. GET NOTIFICATIONS: If user wants to see past notifications → use get_notifications with bookingId
7. CANCEL: If user wants to cancel → use cancel_booking with bookingId

CRITICAL RULES:
1. When booking, you MUST use a slotId from check_availability results. Never make up a slotId.
2. When you successfully create a booking, ALWAYS include the booking ID prominently in your response (e.g., "Your booking is confirmed! Booking ID: PB-XXXXX")
3. When user asks for booking details, ask them for the booking ID if you don't have it already
4. Always extract and store booking IDs from booking results to reference in future messages"""


def merge_dicts(dict1: dict, dict2: dict) -> dict:
    """Merge two dicts, with dict2 values overriding dict1."""
    result = dict1.copy()
    result.update(dict2)
    return result


class GraphState(TypedDict):
    """State for LangGraph agent."""
    messages: Annotated[list[BaseMessage], add_messages]
    sessionContext: Annotated[dict, merge_dicts]
    toolCallLog: Annotated[list, operator.add]


class PawBookGraph:
    """LangGraph-based agent for PawBook."""

    def __init__(self, llm, tools):
        self.llm = llm
        self.tools = {t.name: t for t in tools} if tools else {}
        self.tool_list = tools if tools else []
        self.graph = self._build_graph()

    def _build_graph(self):
        """Build the LangGraph StateGraph."""
        graph = StateGraph(GraphState)

        # Add nodes
        graph.add_node("agent", self.agent_node)
        graph.add_node("tools", ToolNode(self.tool_list))

        # Add edges
        graph.add_edge(START, "agent")
        graph.add_conditional_edges(
            "agent",
            self.should_continue,
            {"continue": "tools", "end": END},
        )
        graph.add_edge("tools", "agent")

        # Compile the graph
        return graph.compile()

    def agent_node(self, state: GraphState) -> GraphState:
        """Agent node that calls the LLM."""
        messages = state.get("messages", [])
        session_context = state.get("sessionContext", {})
        tool_call_log = state.get("toolCallLog", [])

        logger.info(f"Agent node invoked - messages: {len(messages)}, context: {session_context}")

        # Build tool descriptions for the system prompt
        tool_descriptions = "\nAvailable tools:\n"
        for tool_name, tool in self.tools.items():
            tool_descriptions += f"- {tool_name}: {tool.description}\n"

        enhanced_prompt = SYSTEM_PROMPT + tool_descriptions

        # Call LLM with tools
        llm_with_tools = self.llm.bind_tools(self.tool_list)
        full_messages = [SystemMessage(enhanced_prompt)] + messages

        logger.info(f"Calling LLM with {len(full_messages)} messages and {len(self.tools)} tools...")
        response = llm_with_tools.invoke(full_messages)
        logger.info("✅ LLM response received")

        # Extract context from user message
        if messages and isinstance(messages[-1], HumanMessage):
            content = messages[-1].content.lower()
            if "dog" in content and "petType" not in session_context:
                session_context["petType"] = "dog"
                logger.info("  Context: extracted petType=dog")
            elif "cat" in content and "petType" not in session_context:
                session_context["petType"] = "cat"
                logger.info("  Context: extracted petType=cat")
            elif "rabbit" in content and "petType" not in session_context:
                session_context["petType"] = "rabbit"
                logger.info("  Context: extracted petType=rabbit")

        # Extract booking IDs from response content for future reference
        if hasattr(response, 'content') and isinstance(response.content, str):
            # Look for booking ID pattern (e.g., "PB-XXXXXXXX")
            import re
            booking_ids = re.findall(r'PB-[A-F0-9]{8}', response.content)
            if booking_ids and "lastBookingId" not in session_context:
                session_context["lastBookingId"] = booking_ids[0]
                logger.info(f"  Context: extracted lastBookingId={booking_ids[0]}")

        # Log tool calls if present
        if hasattr(response, 'tool_calls') and response.tool_calls:
            logger.info(f"LLM decided to call {len(response.tool_calls)} tool(s)")
            for tc in response.tool_calls:
                logger.info(f"  → {tc.get('name')} with args: {tc.get('args')}")

        return {
            "messages": [response],
            "sessionContext": session_context,
            "toolCallLog": tool_call_log,
        }

    def should_continue(self, state: GraphState) -> str:
        """Determine if we should continue to tool node or end."""
        messages = state.get("messages", [])
        last_message = messages[-1] if messages else None

        # Check if last message has tool calls
        if last_message and hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            logger.info(f"Should continue: YES (found {len(last_message.tool_calls)} tool call(s))")
            return "continue"
        else:
            logger.info("Should continue: NO (no tool calls)")
            return "end"

    def invoke(self, input_state: dict[str, Any]) -> dict[str, Any]:
        """Invoke the graph with input and return final state."""
        logger.info("=== Graph invocation started ===")

        # Prepare state
        state = {
            "messages": input_state.get("messages", []),
            "sessionContext": input_state.get("sessionContext", {}),
            "toolCallLog": input_state.get("toolCallLog", []),
        }

        # Run the graph
        final_state = self.graph.invoke(state)
        logger.info("=== Graph invocation completed ===")

        return final_state


def build_graph(langchain_tools):
    """Build a LangGraph-based agent with Groq API."""
    from langchain_groq import ChatGroq

    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        raise ValueError("GROQ_API_KEY not set in .env file")

    # Use llama-3.1-70b-versatile for better tool calling support
    llm = ChatGroq(
        model=os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile"),
        api_key=groq_key,
        temperature=0.7,
        max_tokens=1024,
    )

    logger.info("🐾 Building PawBook LangGraph agent...")
    logger.info(f"  LLM: {os.getenv('GROQ_MODEL', 'mixtral-8x7b-32768')} (Groq)")
    logger.info(f"  Tools: {len(langchain_tools)}")

    return PawBookGraph(llm, langchain_tools)
