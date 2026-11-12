import os, hmac, hashlib, secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, String, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, Session
from passlib.context import CryptContext
from jose import jwt, JWTError

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ghostbots.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_THIS_TO_A_LONG_RANDOM_SECRET")
ALGORITHM = "HS256"
TOKEN_HOURS = int(os.getenv("TOKEN_HOURS", "24"))
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)

class Base(DeclarativeBase): pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(60), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

class Bot(Base):
    __tablename__ = "bots"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(80))
    description: Mapped[str] = mapped_column(String(240), default="")
    status: Mapped[str] = mapped_column(String(20), default="paused")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

class Contact(Base):
    __tablename__ = "contacts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str] = mapped_column(String(30))
    opted_in: Mapped[bool] = mapped_column(Boolean, default=False)
    consent_source: Mapped[str] = mapped_column(String(200), default="")

class Message(Base):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    contact_id: Mapped[Optional[int]] = mapped_column(ForeignKey("contacts.id"), nullable=True)
    direction: Mapped[str] = mapped_column(String(10), default="out")
    body: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

Base.metadata.create_all(bind=engine)
app = FastAPI(title="GHOST BOTS API", version="2.0.0")
app.mount("/static", StaticFiles(directory="public"), name="static")

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

def current_user(creds: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    if not creds: raise HTTPException(401, "Inicia sesión para continuar")
    try:
        payload = jwt.decode(creds.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(401, "Sesión inválida o vencida")
    user = db.get(User, user_id)
    if not user: raise HTTPException(401, "Usuario no encontrado")
    return user

class AuthInput(BaseModel):
    username: str = Field(min_length=3, max_length=60)
    password: str = Field(min_length=8, max_length=128)

class BotInput(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    description: str = Field(default="", max_length=240)

class ContactInput(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    phone: str = Field(min_length=5, max_length=30)
    opted_in: bool = False
    consent_source: str = Field(default="", max_length=200)

@app.get("/", response_class=HTMLResponse)
def home():
    with open("public/index.html", encoding="utf-8") as f: return f.read()

@app.get("/api/health")
def health(): return {"ok": True, "app": "GHOST BOTS", "version": "2.0.0"}

@app.post("/api/auth/register")
def register(data: AuthInput, db: Session = Depends(get_db)):
    if db.query(User).first():
        raise HTTPException(403, "El registro público está cerrado. Usa la cuenta administradora existente.")
    user = User(username=data.username, password_hash=pwd_context.hash(data.password))
    db.add(user); db.commit(); db.refresh(user)
    token = jwt.encode({"sub": str(user.id), "exp": datetime.now(timezone.utc) + timedelta(hours=TOKEN_HOURS)}, SECRET_KEY, algorithm=ALGORITHM)
    return {"token": token, "username": user.username}

@app.post("/api/auth/login")
def login(data: AuthInput, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not pwd_context.verify(data.password, user.password_hash):
        raise HTTPException(401, "Usuario o contraseña incorrectos")
    token = jwt.encode({"sub": str(user.id), "exp": datetime.now(timezone.utc) + timedelta(hours=TOKEN_HOURS)}, SECRET_KEY, algorithm=ALGORITHM)
    return {"token": token, "username": user.username}

@app.get("/api/me")
def me(user: User = Depends(current_user)):
    return {"id": user.id, "username": user.username}

@app.get("/api/stats")
def stats(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return {"bots": db.query(Bot).filter_by(owner_id=user.id).count(),
            "contacts": db.query(Contact).filter_by(owner_id=user.id).count(),
            "messages": db.query(Message).filter_by(owner_id=user.id).count()}

@app.get("/api/bots")
def list_bots(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return [{"id": b.id, "name": b.name, "description": b.description, "status": b.status} for b in db.query(Bot).filter_by(owner_id=user.id).order_by(Bot.id.desc()).all()]

@app.post("/api/bots")
def create_bot(data: BotInput, user: User = Depends(current_user), db: Session = Depends(get_db)):
    bot = Bot(owner_id=user.id, name=data.name, description=data.description)
    db.add(bot); db.commit(); db.refresh(bot)
    return {"id": bot.id, "name": bot.name, "description": bot.description, "status": bot.status}

@app.patch("/api/bots/{bot_id}")
def update_bot(bot_id: int, data: BotInput, user: User = Depends(current_user), db: Session = Depends(get_db)):
    bot = db.query(Bot).filter_by(id=bot_id, owner_id=user.id).first()
    if not bot: raise HTTPException(404, "Bot no encontrado")
    bot.name, bot.description = data.name, data.description
    db.commit()
    return {"ok": True}

@app.delete("/api/bots/{bot_id}")
def delete_bot(bot_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    bot = db.query(Bot).filter_by(id=bot_id, owner_id=user.id).first()
    if not bot: raise HTTPException(404, "Bot no encontrado")
    db.delete(bot); db.commit()
    return {"ok": True}

@app.get("/api/contacts")
def list_contacts(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return [{"id": c.id, "name": c.name, "phone": c.phone, "opted_in": c.opted_in} for c in db.query(Contact).filter_by(owner_id=user.id).all()]

@app.post("/api/contacts")
def add_contact(data: ContactInput, user: User = Depends(current_user), db: Session = Depends(get_db)):
    contact = Contact(owner_id=user.id, **data.model_dump())
    db.add(contact); db.commit(); db.refresh(contact)
    return {"id": contact.id, "name": contact.name}

@app.post("/api/assistant/draft")
def draft(payload: dict, user: User = Depends(current_user)):
    topic = str(payload.get("topic", "tu consulta"))[:300]
    return {"draft": f"Hola. Gracias por escribirnos sobre {topic}. En breve te compartiremos más información."}

@app.post("/api/whatsapp/send")
async def whatsapp_send(payload: dict, user: User = Depends(current_user), db: Session = Depends(get_db)):
    contact_id = int(payload.get("contact_id", 0))
    body = str(payload.get("body", "")).strip()
    contact = db.query(Contact).filter_by(id=contact_id, owner_id=user.id).first()
    if not contact: raise HTTPException(404, "Contacto no encontrado")
    if not contact.opted_in or not contact.consent_source:
        raise HTTPException(400, "No se puede enviar: falta consentimiento verificable del contacto.")
    token = os.getenv("WHATSAPP_TOKEN")
    phone_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
    if not token or not phone_id: raise HTTPException(503, "WhatsApp Cloud API aún no está configurado.")
    if not body: raise HTTPException(400, "El mensaje está vacío.")
    import httpx
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(f"https://graph.facebook.com/v21.0/{phone_id}/messages",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={"messaging_product":"whatsapp","to":contact.phone,"type":"text","text":{"body":body}})
    if response.status_code >= 400: raise HTTPException(response.status_code, "WhatsApp rechazó el envío.")
    db.add(Message(owner_id=user.id, contact_id=contact.id, body=body, status="sent")); db.commit()
    return {"ok": True, "provider": response.json()}

@app.get("/api/whatsapp/webhook")
def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    if mode == "subscribe" and token and secrets.compare_digest(token, os.getenv("WHATSAPP_VERIFY_TOKEN", "")):
        return JSONResponse(content=challenge or "")
    raise HTTPException(403, "Verificación no válida")

@app.post("/api/whatsapp/webhook")
async def webhook_placeholder(request: Request):
    # Antes de producción, valida X-Hub-Signature-256 y procesa eventos de forma idempotente.
    return {"received": True}
