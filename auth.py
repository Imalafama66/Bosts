from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.config import settings
from src.database import get_db
from src.models import User
from src.schemas import AuthInput
from src.security import current_user, issue_token, pwd_context
router = APIRouter(prefix="/api/auth", tags=["authentication"])

@router.get("/status")
def auth_status(db: Session = Depends(get_db)):
    return {"has_users": db.query(User).first() is not None, "registration_enabled": settings.allow_registration}

@router.post("/register")
def register(data: AuthInput, db: Session = Depends(get_db)):
    if not settings.allow_registration:
        raise HTTPException(403, "El registro está desactivado por el administrador.")
    if db.query(User).filter_by(username=data.username).first():
        raise HTTPException(409, "Ese nombre de usuario ya está en uso.")
    user = User(username=data.username, password_hash=pwd_context.hash(data.password))
    db.add(user)
    try: db.commit()
    except Exception:
        db.rollback(); raise HTTPException(409, "No se pudo crear la cuenta. Prueba con otro usuario.")
    db.refresh(user)
    return {"token": issue_token(user), "username": user.username}

@router.post("/login")
def login(data: AuthInput, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(username=data.username).first()
    if not user or not pwd_context.verify(data.password, user.password_hash):
        raise HTTPException(401, "Usuario o contraseña incorrectos.")
    return {"token": issue_token(user), "username": user.username}

@router.get("/me")
def me(user: User = Depends(current_user)):
    return {"id": user.id, "username": user.username}

