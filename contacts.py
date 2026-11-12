import csv, io
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from src.database import get_db
from src.models import Contact, Message, User
from src.schemas import ContactInput
from src.security import current_user
router = APIRouter(prefix="/api/contacts", tags=["contacts"])

def serialize(c): return {"id":c.id,"name":c.name,"phone":c.phone,"opted_in":c.opted_in,"consent_source":c.consent_source}

@router.get("")
def list_contacts(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return [serialize(c) for c in db.query(Contact).filter_by(owner_id=user.id).order_by(Contact.id.desc()).all()]

@router.post("")
def add_contact(data: ContactInput, user: User = Depends(current_user), db: Session = Depends(get_db)):
    contact = Contact(owner_id=user.id, **data.model_dump()); db.add(contact); db.commit(); db.refresh(contact); return serialize(contact)

@router.patch("/{contact_id}")
def update_contact(contact_id: int, data: ContactInput, user: User = Depends(current_user), db: Session = Depends(get_db)):
    contact = db.query(Contact).filter_by(id=contact_id, owner_id=user.id).first()
    if not contact: raise HTTPException(404, "Contacto no encontrado.")
    for key, value in data.model_dump().items(): setattr(contact, key, value)
    db.commit(); return {"ok": True}

@router.delete("/{contact_id}")
def delete_contact(contact_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    contact = db.query(Contact).filter_by(id=contact_id, owner_id=user.id).first()
    if not contact: raise HTTPException(404, "Contacto no encontrado.")
    db.query(Message).filter_by(owner_id=user.id, contact_id=contact.id).update({"contact_id": None})
    db.delete(contact); db.commit(); return {"ok": True}

@router.get("/export/csv")
def export_contacts(user: User = Depends(current_user), db: Session = Depends(get_db)):
    output = io.StringIO(); writer = csv.writer(output)
    writer.writerow(["nombre", "telefono", "consentimiento", "fuente_consentimiento"])
    for c in db.query(Contact).filter_by(owner_id=user.id).order_by(Contact.id.asc()).all():
        writer.writerow([c.name, c.phone, "si" if c.opted_in else "no", c.consent_source])
    output.seek(0)
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv; charset=utf-8", headers={"Content-Disposition":"attachment; filename=ghostbots-contactos.csv"})

