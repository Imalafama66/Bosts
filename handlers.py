"""Extension points for future event handlers.

Incoming WhatsApp webhook events are signature-verified in src.routes.integrations,
but they are not yet dispatched here. Add validated event adapters before enabling
any automated replies or outbound workflows.
"""

def normalize_event(payload: dict) -> dict:
    return {"object": payload.get("object"), "entries": payload.get("entry", [])}
