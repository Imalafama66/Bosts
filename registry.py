from sqlalchemy.orm import Session
from src.models import Bot

def list_owned(db: Session, owner_id: int):
    return db.query(Bot).filter_by(owner_id=owner_id).order_by(Bot.id.desc()).all()
