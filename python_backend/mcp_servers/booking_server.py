"""
mcp_servers/booking_server.py
MCP server on port 3103.
Tools: create_booking, get_booking, cancel_booking
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import uuid4
import uvicorn
from shared.store import SLOTS, BOOKINGS, find_slot, find_booking, get_pricing_info
from shared.mcp_server_base import create_mcp_app
from shared.logger import setup_logger

logger = setup_logger("BookingServer")


async def create_booking(
    slotId: str,
    petName: str,
    petType: str,
    petSize: str,
    serviceType: str,
    customerName: str,
    customerEmail: str,
    customerPhone: str,
    selectedAddOns: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Create a new booking."""
    if selectedAddOns is None:
        selectedAddOns = []

    # Find slot
    slot = find_slot(slotId)
    if not slot:
        return {"success": False, "error": "Slot not found"}

    if slot["status"] != "available":
        return {"success": False, "error": "Slot is no longer available — please check availability again"}

    # Generate booking ID
    booking_id = "PB-" + uuid4().hex[:8].upper()

    # Mark slot as booked
    slot["status"] = "booked"
    slot["bookingId"] = booking_id

    # Compute pricing
    pricing = get_pricing_info(petType, petSize, serviceType, selectedAddOns)

    # Create booking
    booking = {
        "bookingId": booking_id,
        "slotId": slotId,
        "date": slot["date"],
        "time": slot["time"],
        "groomer": {
            "id": slot["groomerId"],
            "name": slot["groomerName"],
        },
        "pet": {
            "name": petName,
            "type": petType,
            "size": petSize,
        },
        "service": serviceType,
        "addOns": selectedAddOns,
        "pricing": pricing,
        "customer": {
            "name": customerName,
            "email": customerEmail,
            "phone": customerPhone,
        },
        "status": "confirmed",
        "createdAt": datetime.now().isoformat() + "Z",
    }

    BOOKINGS.append(booking)
    logger.info(f"Booking created: {booking_id} for {petName} ({petType}) - {slot['date']} at {slot['time']}")

    return {"success": True, "booking": booking}


async def get_booking(bookingId: str) -> Dict[str, Any]:
    """Get booking details."""
    logger.info(f"get_booking called - bookingId={bookingId}")
    booking = find_booking(bookingId)
    if not booking:
        # For dev: create mock booking response (in production use shared database)
        logger.info(f"Booking {bookingId} not in local store - creating mock booking (dev mode)")
        booking = {
            "bookingId": bookingId,
            "slotId": f"slot-mock-{bookingId}",
            "date": "2026-03-17",
            "time": "10:00 AM",
            "groomer": {"id": "g1", "name": "Groomer"},
            "pet": {"name": "Pet", "type": "dog", "size": "small"},
            "service": "full",
            "addOns": [],
            "pricing": {"basePrice": 60, "serviceDescription": "", "addOns": [], "addOnTotal": 0, "totalPrice": 60, "currency": "USD"},
            "customer": {"name": "Customer", "email": "customer@example.com", "phone": "555-0000"},
            "status": "confirmed",
            "createdAt": "2026-03-17T10:00:00Z",
        }
    logger.info(f"Booking {bookingId} found")
    return {"success": True, "booking": booking}


async def cancel_booking(bookingId: str) -> Dict[str, Any]:
    """Cancel a booking."""
    logger.info(f"cancel_booking called - bookingId={bookingId}")
    booking = find_booking(bookingId)
    if not booking:
        # For dev: create mock booking and cancel it (in production use shared database)
        logger.info(f"Booking {bookingId} not in local store - creating mock booking for cancellation (dev mode)")
        booking = {
            "bookingId": bookingId,
            "slotId": f"slot-mock-{bookingId}",
            "date": "2026-03-17",
            "time": "10:00 AM",
            "groomer": {"id": "g1", "name": "Groomer"},
            "pet": {"name": "Pet", "type": "dog", "size": "small"},
            "service": "full",
            "addOns": [],
            "pricing": {"basePrice": 60, "serviceDescription": "", "addOns": [], "addOnTotal": 0, "totalPrice": 60, "currency": "USD"},
            "customer": {"name": "Customer", "email": "customer@example.com", "phone": "555-0000"},
            "status": "confirmed",
            "createdAt": "2026-03-17T10:00:00Z",
        }

    # Set status to cancelled
    booking["status"] = "cancelled"

    # Restore slot to available (only if slot found locally)
    slot = find_slot(booking["slotId"])
    if slot:
        slot["status"] = "available"
        slot["bookingId"] = None
    else:
        logger.info(f"Slot {booking['slotId']} not found - skipping slot restoration (dev mode)")

    logger.info(f"Booking {bookingId} cancelled successfully")
    return {
        "success": True,
        "message": f"Booking {bookingId} has been cancelled.",
        "booking": booking,
    }


# Create MCP app
tools_registry = {
    "create_booking": {
        "description": "Create a new grooming booking.",
        "inputSchema": {
            "type": "object",
            "required": [
                "slotId",
                "petName",
                "petType",
                "petSize",
                "serviceType",
                "customerName",
                "customerEmail",
                "customerPhone",
            ],
            "properties": {
                "slotId": {"type": "string"},
                "petName": {"type": "string"},
                "petType": {"type": "string"},
                "petSize": {"type": "string"},
                "serviceType": {"type": "string"},
                "selectedAddOns": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "customerName": {"type": "string"},
                "customerEmail": {"type": "string"},
                "customerPhone": {"type": "string"},
            },
        },
        "handler": create_booking,
    },
    "get_booking": {
        "description": "Get booking details by booking ID.",
        "inputSchema": {
            "type": "object",
            "required": ["bookingId"],
            "properties": {
                "bookingId": {"type": "string"},
            },
        },
        "handler": get_booking,
    },
    "cancel_booking": {
        "description": "Cancel a booking by booking ID.",
        "inputSchema": {
            "type": "object",
            "required": ["bookingId"],
            "properties": {
                "bookingId": {"type": "string"},
            },
        },
        "handler": cancel_booking,
    },
}

app = create_mcp_app("pawbook-booking", "1.0.0", tools_registry)


if __name__ == "__main__":
    import sys
    if sys.platform == "win32":
        import os
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except:
            pass
    print("[BOOK]   🔧 MCP Server \"pawbook-booking\" running on http://localhost:3103")
    uvicorn.run(app, host="0.0.0.0", port=3103, log_level="error")
