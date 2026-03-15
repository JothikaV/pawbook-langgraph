"""
mcp_servers/pricing_server.py
MCP server on port 3102.
Tools: get_pricing, list_addons
"""
from typing import List, Optional, Dict, Any
import uvicorn
from shared.store import PRICING, ADDONS, get_pricing_info
from shared.mcp_server_base import create_mcp_app
from shared.logger import setup_logger

logger = setup_logger("PricingServer")


async def get_pricing(
    petType: str,
    petSize: str,
    serviceType: str,
    selectedAddOns: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Get pricing for a grooming service."""
    logger.info(f"get_pricing called - petType={petType}, petSize={petSize}, serviceType={serviceType}, addons={selectedAddOns}")

    if selectedAddOns is None:
        selectedAddOns = []

    pricing_info = get_pricing_info(petType, petSize, serviceType, selectedAddOns)
    logger.info(f"get_pricing returned price=${pricing_info.get('totalPrice')}")

    return {
        "success": True,
        "pricing": pricing_info,
        "availableAddOns": [
            {"id": a["id"], "name": a["name"], "price": a["price"]}
            for a in ADDONS
        ],
    }


async def list_addons() -> Dict[str, Any]:
    """List all available add-ons."""
    logger.info(f"list_addons called - returning {len(ADDONS)} add-ons")
    return {
        "success": True,
        "addons": [
            {"id": a["id"], "name": a["name"], "price": a["price"]}
            for a in ADDONS
        ],
    }


# Create MCP app
tools_registry = {
    "get_pricing": {
        "description": "Get pricing for a grooming service.",
        "inputSchema": {
            "type": "object",
            "required": ["petType", "petSize", "serviceType"],
            "properties": {
                "petType": {
                    "type": "string",
                    "description": '"dog" | "cat" | "rabbit"',
                },
                "petSize": {
                    "type": "string",
                    "description": '"small" | "medium" | "large" | "giant"',
                },
                "serviceType": {
                    "type": "string",
                    "description": '"basic" | "full" | "bath_only"',
                },
                "selectedAddOns": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": 'e.g. ["nail_trim", "paw_balm"]',
                },
            },
        },
        "handler": get_pricing,
    },
    "list_addons": {
        "description": "List all available add-ons.",
        "inputSchema": {"type": "object"},
        "handler": list_addons,
    },
}

app = create_mcp_app("pawbook-pricing", "1.0.0", tools_registry)


if __name__ == "__main__":
    import sys
    if sys.platform == "win32":
        import os
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except:
            pass
    print("[PRICE]   🔧 MCP Server \"pawbook-pricing\" running on http://localhost:3102")
    uvicorn.run(app, host="0.0.0.0", port=3102, log_level="error")
