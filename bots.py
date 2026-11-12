from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db
from src.models import Bot, User
from src.schemas import BotInput
from src.security import current_user
router = APIRouter(prefix="/api/bots", tags=["bots"])

def serialize(bot): return {"id": bot.id, "name": bot.name, "description": bot.description, "status": bot.status}

@router.get("")
def list_bots(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return [serialize(b) for b in db.query(Bot).filter_by(owner_id=user.id).order_by(Bot.id.desc()).all()]

@router.post("")
def create_bot(data: BotInput, user: User = Depends(current_user), db: Session = Depends(get_db)):
    bot = Bot(owner_id=user.id, name=data.name, description=data.description); db.add(bot); db.commit(); db.refresh(bot)
    return serialize(bot)

@router.patch("/{bot_id}")
def update_bot(bot_id: int, data: BotInput, user: User = Depends(current_user), db: Session = Depends(get_db)):
    bot = db.query(Bot).filter_by(id=bot_id, owner_id=user.id).first()
    if not bot: raise HTTPException(404, "Bot no encontrado.")
    bot.name, bot.description = data.name, data.description; db.commit(); return {"ok": True}

@router.patch("/{bot_id}/status")
def set_status(bot_id: int, payload: dict, user: User = Depends(current_user), db: Session = Depends(get_db)):
    status = str(payload.get("status", ""))
    if status not in {"active", "paused"}: raise HTTPException(400, "Estado no válido.")
    bot = db.query(Bot).filter_by(id=bot_id, owner_id=user.id).first()
    if not bot: raise HTTPException(404, "Bot no encontrado.")
    bot.status = status; db.commit(); return {"ok": True, "status": status}

@router.delete("/{bot_id}")
def delete_bot(bot_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    bot = db.query(Bot).filter_by(id=bot_id, owner_id=user.id).first()
    if not bot: raise HTTPException(404, "Bot no encontrado.")
    db.delete(bot); db.commit(); return {"ok": True}
