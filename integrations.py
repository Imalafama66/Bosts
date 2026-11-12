import hashlib, hmac, secrets
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from src.config import settings
router = APIRouter(prefix="/api/whatsapp", tags=["integrations"])

@router.get("/webhook")
def verify_webhook(request: Request):
    q = request.query_params
    if q.get("hub.mode") == "subscribe" and settings.whatsapp_verify_token and secrets.compare_digest(q.get("hub.verify_token", ""), settings.whatsapp_verify_token):
        return JSONResponse(content=q.get("hub.challenge", ""))
    raise HTTPException(403, "Verificación no válida.")

@router.post("/webhook")
async def whatsapp_webhook(request: Request):
    body = await request.body(); signature = request.headers.get("X-Hub-Signature-256", "")
    if not settings.whatsapp_app_secret: raise HTTPException(503, "Configura WHATSAPP_APP_SECRET para validar el webhook.")
    expected = "sha256=" + hmac.new(settings.whatsapp_app_secret.encode(), body, hashlib.sha256).hexdigest()
    if not signature or not hmac.compare_digest(signature, expected): raise HTTPException(403, "Firma de webhook no válida.")
    return {"received": True, "note": "Firma validada; el procesamiento de eventos entrantes aún no está implementado."}
