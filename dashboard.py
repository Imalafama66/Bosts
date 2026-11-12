from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from src.config import settings
from src.database import get_db
from src.models import Bot, Contact, Message, User
from src.security import current_user
from src.services.assistant import make_draft
router = APIRouter(tags=["dashboard"])

@router.get("/api/stats")
def stats(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return {"bots":db.query(Bot).filter_by(owner_id=user.id).count(),"contacts":db.query(Contact).filter_by(owner_id=user.id).count(),"messages":db.query(Message).filter_by(owner_id=user.id).count()}

@router.get("/api/system/status")
def system_status(user: User = Depends(current_user), db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"api":"online","database":"online","whatsapp":bool(settings.whatsapp_token and settings.whatsapp_phone_number_id),"version":"5.0.0"}

@router.post("/api/assistant/draft")
def draft(payload: dict, user: User = Depends(current_user)):
    return {"draft":make_draft(str(payload.get("topic", "tu consulta")))}

@router.get("/api/integrations/whatsapp/status")
def whatsapp_status(user: User = Depends(current_user)):
    return {"configured":bool(settings.whatsapp_token and settings.whatsapp_phone_number_id),"phone_number_id":bool(settings.whatsapp_phone_number_id)}
