from sqlalchemy.orm import Session
from src.models import Bot

class BotProfileManager:
    """CRUD helper for stored bot profiles; it does not run external bot processes."""
    @staticmethod
    def get(db: Session, owner_id: int, bot_id: int):
        return db.query(Bot).filter_by(id=bot_id, owner_id=owner_id).first()

    @staticmethod
    def set_status(db: Session, owner_id: int, bot_id: int, status: str):
        if status not in {"active", "paused"}:
            raise ValueError("status must be active or paused")
        bot = BotProfileManager.get(db, owner_id, bot_id)
        if bot is None:
            return None
        bot.status = status
        db.commit()
        return bot
