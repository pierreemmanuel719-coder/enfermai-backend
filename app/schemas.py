from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from app.models.models import TriagemEnum, StatusEnum

# ─── Auth ───────────────────────────────────────────────────────────────────
class UserCreate(BaseModel):
    nome: str
    email: EmailStr
    password: str
    coren: Optional[str] = None
    funcao: Optional[str] = None
    setor: Optional[str] = None

class UserOut(BaseModel):
    id: int
    nome: str
    email: str
    coren: Optional[str]
    funcao: Optional[str]
    setor: Optional[str]
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut

class LoginForm(BaseModel):
    email: EmailStr
    password: str

# ─── Vital Signs ─────────────────────────────────────────────────────────────
class VitalSignCreate(BaseModel):
    pa_sistol:   Optional[int]   = None
    pa_diast:    Optional[int]   = None
    fc:          Optional[int]   = None
    temperatura: Optional[float] = None
    spo2:        Optional[float] = None
    fr:          Optional[int]   = None
    glicemia:    Optional[float] = None

class VitalSignOut(VitalSignCreate):
    id: int
    patient_id: int
    registered_at: datetime
    class Config:
        from_attributes = True

# ─── Medications ─────────────────────────────────────────────────────────────
class MedicationCreate(BaseModel):
    nome: str
    dose: Optional[str] = None
    frequencia: Optional[str] = None
    via: Optional[str] = None

class MedicationOut(MedicationCreate):
    id: int
    patient_id: int
    prescrito_em: datetime
    class Config:
        from_attributes = True

# ─── Exams ───────────────────────────────────────────────────────────────────
class ExamCreate(BaseModel):
    nome: str
    resultado: Optional[str] = None
    status: Optional[str] = "Pendente"

class ExamOut(ExamCreate):
    id: int
    patient_id: int
    realizado_em: datetime
    class Config:
        from_attributes = True

# ─── Patients ────────────────────────────────────────────────────────────────
class PatientCreate(BaseModel):
    nome: str
    leito: str
    idade: Optional[int] = None
    sexo: Optional[str] = None
    triagem: Optional[TriagemEnum] = TriagemEnum.green
    status: Optional[StatusEnum] = StatusEnum.internado
    diagnostico: Optional[str] = None
    medico_resp: Optional[str] = None
    alergias: Optional[str] = None
    comorbidades: Optional[str] = None
    anamnese: Optional[str] = None

class PatientUpdate(PatientCreate):
    nome: Optional[str] = None
    leito: Optional[str] = None

class PatientOut(BaseModel):
    id: int
    nome: str
    leito: str
    idade: Optional[int]
    sexo: Optional[str]
    triagem: TriagemEnum
    status: StatusEnum
    diagnostico: Optional[str]
    medico_resp: Optional[str]
    alergias: Optional[str]
    comorbidades: Optional[str]
    anamnese: Optional[str]
    admissao: datetime
    vitais: List[VitalSignOut] = []
    medicamentos: List[MedicationOut] = []
    exames: List[ExamOut] = []
    class Config:
        from_attributes = True

# ─── SOAP ────────────────────────────────────────────────────────────────────
class SOAPCreate(BaseModel):
    subjetivo: Optional[str] = None
    objetivo:  Optional[str] = None
    avaliacao: Optional[str] = None
    plano:     Optional[str] = None
    gerado_ia: Optional[int] = 0

class SOAPOut(SOAPCreate):
    id: int
    patient_id: int
    created_at: datetime
    class Config:
        from_attributes = True

# ─── Timeline ────────────────────────────────────────────────────────────────
class TimelineEventCreate(BaseModel):
    descricao: str
    tipo: Optional[str] = "geral"

class TimelineEventOut(TimelineEventCreate):
    id: int
    patient_id: int
    created_at: datetime
    class Config:
        from_attributes = True

# ─── AI ──────────────────────────────────────────────────────────────────────
class AIRequest(BaseModel):
    prompt: str

class AIResponse(BaseModel):
    resultado: str
