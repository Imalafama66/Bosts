from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db
from src.models import Contact, Message, User
from src.schemas import MessageInput
from src.security import current_user
from src.services.whatsapp import send_text
router = APIRouter(tags=["messages"])

@router.get("/api/messages")
def list_messages(user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = db.query(Message).filter_by(owner_id=user.id).order_by(Message.id.desc()).limit(100).all()
    contacts = {c.id:c.name for c in db.query(Contact).filter_by(owner_id=user.id).all()}
    return [{"id":m.id,"contact":contacts.get(m.contact_id,"Contacto"),"direction":m.direction,"body":m.body,"status":m.status,"created_at":m.created_at.isoformat()} for m in rows]

@router.get("/api/activity")
def activity(user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = db.query(Message).filter_by(owner_id=user.id).order_by(Message.id.desc()).limit(8).all()
    contacts = {c.id:c.name for c in db.query(Contact).filter_by(owner_id=user.id).all()}
    return [{"id":m.id,"contact":contacts.get(m.contact_id,"Contacto"),"direction":m.direction,"body":m.body[:180],"status":m.status,"created_at":m.created_at.isoformat()} for m in rows]

@router.post("/api/whatsapp/send")
async def whatsapp_send(payload: MessageInput, user: User = Depends(current_user), db: Session = Depends(get_db)):
    contact = db.query(Contact).filter_by(id=payload.contact_id, owner_id=user.id).first()
    if not contact: raise HTTPException(404, "Contacto no encontrado.")
    if not contact.opted_in or not contact.consent_source:
        raise HTTPException(400, "Este contacto no tiene consentimiento registrado. No se enviará el mensaje.")
    result = await send_text(contact.phone, payload.body)
    provider_id = (result.get("messages") or [{}])[0].get("id")
    message = Message(owner_id=user.id, contact_id=contact.id, body=payload.body, status="sent", provider_id=provider_id)
    db.add(message); db.commit(); db.refresh(message)
    return {"ok":True,"message_id":message.id,"provider_id":provider_id}
