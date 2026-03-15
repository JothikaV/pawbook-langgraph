"""
shared/store.py
In-memory data store for PawBook MCP servers.
All data is module-level, so each process gets its own copy.
"""
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any

# ─── GROOMERS ─────────────────────────────────────────────
GROOMERS = [
    {"id": "g1", "name": "Sarah Chen", "specialties": ["dog", "cat"], "rating": 4.9},
    {"id": "g2", "name": "Marcus Rivera", "specialties": ["dog", "rabbit"], "rating": 4.8},
    {"id": "g3", "name": "Priya Nair", "specialties": ["cat"], "rating": 4.7},
    {"id": "g4", "name": "Tom Walsh", "specialties": ["dog"], "rating": 4.6},
]

# ─── PRICING MATRIX (USD) ─────────────────────────────────
PRICING = {
    "dog": {
        "small": {"basic": 35, "full": 60, "bath_only": 25},
        "medium": {"basic": 45, "full": 75, "bath_only": 35},
        "large": {"basic": 55, "full": 90, "bath_only": 45},
        "giant": {"basic": 70, "full": 110, "bath_only": 55},
    },
    "cat": {
        "small": {"basic": 40, "full": 65, "bath_only": 30},
        "medium": {"basic": 50, "full": 75, "bath_only": 38},
        "large": {"basic": 60, "full": 85, "bath_only": 45},
    },
    "rabbit": {
        "small": {"basic": 30, "full": 50, "bath_only": 20},
        "medium": {"basic": 38, "full": 60, "bath_only": 28},
    },
}

# ─── ADD-ONS ───────────────────────────────────────────────
ADDONS = [
    {"id": "nail_trim", "name": "Nail Trimming", "price": 10},
    {"id": "teeth_brushing", "name": "Teeth Brushing", "price": 12},
    {"id": "flea_treatment", "name": "Flea Treatment", "price": 20},
    {"id": "bow_accessory", "name": "Bow / Bandana", "price": 5},
    {"id": "paw_balm", "name": "Paw Balm", "price": 8},
]

# ─── BOOKINGS & NOTIFICATIONS ────────────────────────────
BOOKINGS: List[Dict[str, Any]] = []
NOTIFICATIONS: List[Dict[str, Any]] = []

# ─── SLOTS (generated on import) ────────────────────────
SLOTS: List[Dict[str, Any]] = []

# ─── UTILITY FUNCTIONS ────────────────────────────────────

def _generate_slots():
    """Generate slots for 7 days × 7 times × 4 groomers - deterministic generation."""
    times = ["9:00 AM", "10:30 AM", "12:00 PM", "2:00 PM", "3:30 PM", "5:00 PM", "6:30 PM"]

    start_date = datetime.now().date()
    slots = []
    slot_idx = 0

    for day_offset in range(7):
        date = start_date + timedelta(days=day_offset)
        date_str = date.isoformat()

        for time_slot in times:
            for groomer in GROOMERS:
                slot_id = f"slot-{date_str}-{groomer['id']}-{slot_idx}"
                slot_idx += 1

                # Deterministic: mark every 3rd slot as booked, rest available
                # This ensures consistent availability across restarts
                is_available = slot_idx % 3 != 0

                slots.append({
                    "id": slot_id,
                    "slotId": slot_id,
                    "date": date_str,
                    "time": time_slot,
                    "groomerId": groomer["id"],
                    "groomerName": groomer["name"],
                    "groomerRating": groomer["rating"],
                    "status": "available" if is_available else "booked",
                    "bookingId": None,
                })

    return slots


def get_pricing_info(pet_type: str, pet_size: str, service_type: str, selected_addons: List[str] = None) -> Dict[str, Any]:
    """Compute pricing breakdown for a grooming service."""
    if selected_addons is None:
        selected_addons = []

    base_price = PRICING.get(pet_type, {}).get(pet_size, {}).get(service_type, 0)

    addons_breakdown = []
    addon_total = 0
    for addon_id in selected_addons:
        addon = next((a for a in ADDONS if a["id"] == addon_id), None)
        if addon:
            addons_breakdown.append({"id": addon["id"], "name": addon["name"], "price": addon["price"]})
            addon_total += addon["price"]

    return {
        "basePrice": base_price,
        "serviceDescription": {
            "basic": "Brush, bath, dry, basic trim",
            "full": "Full groom: brush, bath, dry, full trim, nail care",
            "bath_only": "Bath and dry only",
        }.get(service_type, ""),
        "addOns": addons_breakdown,
        "addOnTotal": addon_total,
        "totalPrice": base_price + addon_total,
        "currency": "USD",
    }


def find_slot(slot_id: str) -> Dict[str, Any] | None:
    """Find a slot by slotId."""
    return next((s for s in SLOTS if s["slotId"] == slot_id), None)


def find_booking(booking_id: str) -> Dict[str, Any] | None:
    """Find a booking by bookingId."""
    return next((b for b in BOOKINGS if b["bookingId"] == booking_id), None)


# Initialize slots on import
SLOTS = _generate_slots()
