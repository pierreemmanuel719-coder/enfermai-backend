from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.models import Patient, VitalSign, Medication, Exam, TimelineEvent, User
from app.schemas import (
    PatientCreate, PatientUpdate, PatientOut,
    VitalSignCreate, VitalSignOut,
    MedicationCreate, MedicationOut,
    ExamCreate, ExamOut,
    TimelineEventCreate, TimelineEventOut,
)
from app.auth import get_current_user

router = APIRouter()

# ─── Pacientes ───────────────────────────────────────────────────────────────

@router.get("/", response_model=List[PatientOut])
def list_patients(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Patient).order_by(Patient.admissao.desc()).all()

@router.post("/", response_model=PatientOut, status_code=201)
def create_patient(data: PatientCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    patient = Patient(**data.dict())
    db.add(patient)
    db.commit()
    db.refresh(patient)
    # Registrar na timeline
    event = TimelineEvent(patient_id=patient.id, descricao="Admissão realizada", tipo="geral")
    db.add(event)
    db.commit()
    return patient

@router.get("/{patient_id}", response_model=PatientOut)
def get_patient(patient_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    p = db.query(Patient).filter(Patient.id == patient_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    return p

@router.patch("/{patient_id}", response_model=PatientOut)
def update_patient(patient_id: int, data: PatientUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    p = db.query(Patient).filter(Patient.id == patient_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    for k, v in data.dict(exclude_unset=True).items():
        setattr(p, k, v)
    db.commit()
    db.refresh(p)
    return p

@router.delete("/{patient_id}", status_code=204)
def delete_patient(patient_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    p = db.query(Patient).filter(Patient.id == patient_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    db.delete(p)
    db.commit()

# ─── Sinais Vitais ────────────────────────────────────────────────────────────

@router.get("/{patient_id}/vitais", response_model=List[VitalSignOut])
def list_vitals(patient_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(VitalSign).filter(VitalSign.patient_id == patient_id).order_by(VitalSign.registered_at.desc()).all()

@router.post("/{patient_id}/vitais", response_model=VitalSignOut, status_code=201)
def add_vital(patient_id: int, data: VitalSignCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _check_patient(patient_id, db)
    vital = VitalSign(patient_id=patient_id, **data.dict())
    db.add(vital)
    # Timeline
    pa_str = f"PA {data.pa_sistol}/{data.pa_diast}" if data.pa_sistol else ""
    fc_str = f"FC {data.fc}bpm" if data.fc else ""
    evento = TimelineEvent(patient_id=patient_id, descricao=f"Sinais vitais registrados · {pa_str} {fc_str}".strip(), tipo="geral")
    db.add(evento)
    db.commit()
    db.refresh(vital)
    return vital

# ─── Medicamentos ────────────────────────────────────────────────────────────

@router.get("/{patient_id}/meds", response_model=List[MedicationOut])
def list_meds(patient_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Medication).filter(Medication.patient_id == patient_id).all()

@router.post("/{patient_id}/meds", response_model=MedicationOut, status_code=201)
def add_med(patient_id: int, data: MedicationCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _check_patient(patient_id, db)
    med = Medication(patient_id=patient_id, **data.dict())
    db.add(med)
    db.commit()
    db.refresh(med)
    return med

@router.delete("/{patient_id}/meds/{med_id}", status_code=204)
def delete_med(patient_id: int, med_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    med = db.query(Medication).filter(Medication.id == med_id, Medication.patient_id == patient_id).first()
    if not med:
        raise HTTPException(status_code=404, detail="Medicamento não encontrado")
    db.delete(med)
    db.commit()

# ─── Exames ───────────────────────────────────────────────────────────────────

@router.get("/{patient_id}/exames", response_model=List[ExamOut])
def list_exams(patient_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Exam).filter(Exam.patient_id == patient_id).all()

@router.post("/{patient_id}/exames", response_model=ExamOut, status_code=201)
def add_exam(patient_id: int, data: ExamCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _check_patient(patient_id, db)
    exam = Exam(patient_id=patient_id, **data.dict())
    db.add(exam)
    db.commit()
    db.refresh(exam)
    return exam

@router.patch("/{patient_id}/exames/{exam_id}", response_model=ExamOut)
def update_exam(patient_id: int, exam_id: int, data: ExamCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    exam = db.query(Exam).filter(Exam.id == exam_id, Exam.patient_id == patient_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exame não encontrado")
    for k, v in data.dict(exclude_unset=True).items():
        setattr(exam, k, v)
    db.commit()
    db.refresh(exam)
    return exam

# ─── Timeline ─────────────────────────────────────────────────────────────────

@router.get("/{patient_id}/timeline", response_model=List[TimelineEventOut])
def list_timeline(patient_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(TimelineEvent).filter(TimelineEvent.patient_id == patient_id).order_by(TimelineEvent.created_at).all()

@router.post("/{patient_id}/timeline", response_model=TimelineEventOut, status_code=201)
def add_timeline(patient_id: int, data: TimelineEventCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _check_patient(patient_id, db)
    event = TimelineEvent(patient_id=patient_id, **data.dict())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event

# ─── Helper ───────────────────────────────────────────────────────────────────

def _check_patient(patient_id: int, db: Session):
    if not db.query(Patient).filter(Patient.id == patient_id).first():
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
