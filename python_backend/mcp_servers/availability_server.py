"""
mcp_servers/availability_server.py
MCP server on port 3101.
Tools: check_availability, list_groomers
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import uvicorn
from shared.store import SLOTS, GROOMERS
from shared.mcp_server_base import create_mcp_app
from shared.logger import setup_logger

logger = setup_logger("AvailabilityServer")


async def check_availability(
    date: Optional[str] = None,
    timePreference: Optional[str] = None,
    petType: Optional[str] = None,
) -> Dict[str, Any]:
    """Check available grooming slots."""
    logger.info(f"check_availability called - date={date}, timePreference={timePreference}, petType={petType}")

    # Parse date
    if date == "today":
        date_filter = datetime.now().date().isoformat()
    elif date == "tomorrow":
        date_filter = (datetime.now().date() + timedelta(days=1)).isoformat()
    elif date == "this weekend":
        date_filter = None  # No date filter
    else:
        date_filter = date

    # Time preference mapping
    time_map = {
        "morning": ["9:00 AM", "10:30 AM"],
        "afternoon": ["12:00 PM", "2:00 PM", "3:30 PM"],
        "evening": ["5:00 PM", "6:30 PM"],
        "any": [],
    }
    allowed_times = time_map.get(timePreference, []) if timePreference else []

    # Filter slots
    filtered = []
    for slot in SLOTS:
        # Date filter
        if date_filter and slot["date"] != date_filter:
            continue

        # Time filter
        if allowed_times and slot["time"] not in allowed_times:
            continue

        # Status filter
        if slot["status"] != "available":
            continue

        # Pet type filter (check groomer specialties)
        if petType:
            groomer = next((g for g in GROOMERS if g["id"] == slot["groomerId"]), None)
            if not groomer or petType not in groomer["specialties"]:
                continue

        filtered.append(slot)

    # Limit to 6 slots
    filtered = filtered[:6]
    logger.info(f"check_availability returned {len(filtered)} slots")

    return {
        "success": True,
        "totalFound": len(filtered),
        "slots": [
            {
                "slotId": s["slotId"],
                "date": s["date"],
                "time": s["time"],
                "groomerId": s["groomerId"],
                "groomerName": s["groomerName"],
                "groomerRating": s["groomerRating"],
            }
            for s in filtered
        ],
    }


async def list_groomers() -> Dict[str, Any]:
    """List all groomers."""
    logger.info(f"list_groomers called - returning {len(GROOMERS)} groomers")
    return {
        "success": True,
        "groomers": [
            {
                "id": g["id"],
                "name": g["name"],
                "specialties": g["specialties"],
                "rating": g["rating"],
            }
            for g in GROOMERS
        ],
    }


# Create MCP app
tools_registry = {
    "check_availability": {
        "description": "Check available grooming slots by date, time preference, and pet type.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": '"today" | "tomorrow" | "this weekend" | "YYYY-MM-DD"',
                },
                "timePreference": {
                    "type": "string",
                    "description": '"morning" | "afternoon" | "evening" | "any"',
                },
                "petType": {
                    "type": "string",
                    "description": '"dog" | "cat" | "rabbit"',
                },
            },
        },
        "handler": check_availability,
    },
    "list_groomers": {
        "description": "List all available groomers.",
        "inputSchema": {"type": "object"},
        "handler": list_groomers,
    },
}

app = create_mcp_app("pawbook-availability", "1.0.0", tools_registry)


if __name__ == "__main__":
    import sys
    # Fix Windows encoding
    if sys.platform == "win32":
        import os
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except:
            pass
    print("[AVAIL]   🔧 MCP Server \"pawbook-availability\" running on http://localhost:3101")
    uvicorn.run(app, host="0.0.0.0", port=3101, log_level="error")
