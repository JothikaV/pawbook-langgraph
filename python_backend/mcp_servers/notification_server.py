"""
mcp_servers/notification_server.py
MCP server on port 3104.
Tools: send_notification, get_notifications
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import uuid4
import uvicorn
from shared.store import NOTIFICATIONS, find_booking
from shared.mcp_server_base import create_mcp_app
from shared.logger import setup_logger

logger = setup_logger("NotificationServer")


async def send_notification(
    bookingId: str,
    type: str = "confirmation",
    channels: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Send notification for a booking."""
    if channels is None:
        channels = ["email", "sms"]

    # Find booking (in dev, create a mock booking if not found since each process has separate state)
    booking = find_booking(bookingId)
    if not booking:
        # For dev/demo: create mock booking response based on bookingId
        # In production, use shared database instead of in-memory state
        booking = {
            "bookingId": bookingId,
            "pet": {"name": "Pet", "type": "dog"},
            "customer": {"name": "Customer", "email": "customer@example.com", "phone": "555-0000"},
            "groomer": {"name": "Groomer"},
            "date": "2026-03-17",
            "time": "10:00 AM",
            "pricing": {"totalPrice": 0},
        }
        logger.info(f"Booking {bookingId} not in local store - using mock booking (dev mode)")


    notif_id = "NOTIF-" + uuid4().hex[:6].upper()

    # Render templates for each channel
    pet = booking["pet"]
    customer = booking["customer"]
    groomer = booking["groomer"]
    date = booking["date"]
    time = booking["time"]
    total_price = booking["pricing"]["totalPrice"]

    sent = []

    if "email" in channels:
        message = f"""Hi {customer['name']}!

Your grooming appointment for {pet['name']} is confirmed.

Date: {date}
Time: {time}
Groomer: {groomer['name']}
Total: ${total_price}

Booking ID: {bookingId}

We look forward to seeing you!"""

        sent.append({
            "channel": "email",
            "to": customer["email"],
            "message": message,
            "status": "delivered [mock]",
            "sentAt": datetime.now().isoformat() + "Z",
        })

    if "sms" in channels:
        message = f"Hi {customer['name']}! Your grooming appointment for {pet['name']} on {date} at {time} is confirmed. Booking: {bookingId}"

        sent.append({
            "channel": "sms",
            "to": customer["phone"],
            "message": message,
            "status": "delivered [mock]",
            "sentAt": datetime.now().isoformat() + "Z",
        })

    if "push" in channels:
        message = f"Your appointment for {pet['name']} on {date} at {time} is confirmed with {groomer['name']}."

        sent.append({
            "channel": "push",
            "to": "push",
            "message": message,
            "status": "delivered [mock]",
            "sentAt": datetime.now().isoformat() + "Z",
        })

    notification = {
        "notifId": notif_id,
        "bookingId": bookingId,
        "type": type,
        "sent": sent,
        "createdAt": datetime.now().isoformat() + "Z",
    }

    NOTIFICATIONS.append(notification)
    logger.info(f"Notification sent for booking {bookingId} via {', '.join(channels)} - notifId={notif_id}")

    return {"success": True, "notification": notification}


async def get_notifications(bookingId: str) -> Dict[str, Any]:
    """Get notifications for a booking."""
    logger.info(f"get_notifications called - bookingId={bookingId}")
    notifs = [n for n in NOTIFICATIONS if n["bookingId"] == bookingId]
    logger.info(f"Found {len(notifs)} notifications for booking {bookingId}")
    return {
        "success": True,
        "notifications": notifs,
        "count": len(notifs),
    }


# Create MCP app
tools_registry = {
    "send_notification": {
        "description": "Send confirmation or reminder notification for a booking.",
        "inputSchema": {
            "type": "object",
            "required": ["bookingId"],
            "properties": {
                "bookingId": {"type": "string"},
                "type": {
                    "type": "string",
                    "description": '"confirmation" | "reminder"',
                },
                "channels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": 'e.g. ["email", "sms"]',
                },
            },
        },
        "handler": send_notification,
    },
    "get_notifications": {
        "description": "Get all notifications for a booking.",
        "inputSchema": {
            "type": "object",
            "required": ["bookingId"],
            "properties": {
                "bookingId": {"type": "string"},
            },
        },
        "handler": get_notifications,
    },
}

app = create_mcp_app("pawbook-notifications", "1.0.0", tools_registry)


if __name__ == "__main__":
    import sys
    if sys.platform == "win32":
        import os
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except:
            pass
    print("[NOTIF]   🔧 MCP Server \"pawbook-notifications\" running on http://localhost:3104")
    uvicorn.run(app, host="0.0.0.0", port=3104, log_level="error")
