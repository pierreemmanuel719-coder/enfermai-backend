from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.models import SOAPNote, User
from app.schemas import SOAPCreate, SOAPOut
from app.auth import get_current_user

router = APIRouter()

@router.get("/{patient_id}", response_model=List[SOAPOut])
def list_soaps(patient_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(SOAPNote).filter(SOAPNote.patient_id == patient_id).order_by(SOAPNote.created_at.desc()).all()

@router.post("/{patient_id}", response_model=SOAPOut, status_code=201)
def save_soap(patient_id: int, data: SOAPCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    note = SOAPNote(patient_id=patient_id, user_id=current_user.id, **data.dict())
    db.add(note)
    db.commit()
    db.refresh(note)
    return note

@router.get("/{patient_id}/{note_id}", response_model=SOAPOut)
def get_soap(patient_id: int, note_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    note = db.query(SOAPNote).filter(SOAPNote.id == note_id, SOAPNote.patient_id == patient_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Nota SOAP não encontrada")
    return note
