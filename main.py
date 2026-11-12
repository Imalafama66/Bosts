from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Depends
from fastapi.responses import FileResponse, StreamingResponse
import csv, io
from sqlalchemy.orm import Session
from src.database import get_db
from fastapi.staticfiles import StaticFiles
from src.database import Base, engine
from src import models  # noqa: F401 - registers ORM metadata
from src.routes import auth, bots, contacts, messages, dashboard, integrations
from src.security import current_user
from src.models import User

BASE_DIR = Path(__file__).resolve().parent

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="GHOST BOTS API", version="5.0.0", description="GHOST BOTS PRO modular command center", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "public")), name="static")
for route_module in (auth, bots, contacts, messages, dashboard, integrations):
    app.include_router(route_module.router)

@app.get("/", include_in_schema=False)
def home():
    return FileResponse(BASE_DIR / "public" / "index.html")

@app.get("/api/me", tags=["authentication"], include_in_schema=False)
def current_account(user: User = Depends(current_user)):
    return {"id": user.id, "username": user.username}

@app.get("/api/export/contacts", include_in_schema=False)
def legacy_export_contacts(user: User = Depends(current_user), db: Session = Depends(get_db)):
    from src.models import Contact
    output = io.StringIO(); writer = csv.writer(output)
    writer.writerow(["nombre", "telefono", "consentimiento", "fuente_consentimiento"])
    for c in db.query(Contact).filter_by(owner_id=user.id).order_by(Contact.id.asc()).all():
        writer.writerow([c.name, c.phone, "si" if c.opted_in else "no", c.consent_source])
    output.seek(0)
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv; charset=utf-8", headers={"Content-Disposition":"attachment; filename=ghostbots-contactos.csv"})

@app.get("/api/health", tags=["system"])
def health():
    return {"ok": True, "app": "GHOST BOTS", "version": "5.0.0"}
