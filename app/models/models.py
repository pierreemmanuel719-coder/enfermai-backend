from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class TriagemEnum(str, enum.Enum):
    red    = "red"
    orange = "orange"
    yellow = "yellow"
    green  = "green"

class StatusEnum(str, enum.Enum):
    internado   = "Internado"
    critico     = "Crítico"
    alta_prev   = "Alta prev."
    observacao  = "Obs."

class User(Base):
    __tablename__ = "users"
    id           = Column(Integer, primary_key=True, index=True)
    nome         = Column(String(120), nullable=False)
    email        = Column(String(120), unique=True, index=True, nullable=False)
    coren        = Column(String(20))
    funcao       = Column(String(80))
    setor        = Column(String(80))
    hashed_pass  = Column(String(200), nullable=False)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())

class Patient(Base):
    __tablename__ = "patients"
    id           = Column(Integer, primary_key=True, index=True)
    nome         = Column(String(120), nullable=False)
    leito        = Column(String(20), nullable=False)
    idade        = Column(Integer)
    sexo         = Column(String(1))  # M / F / O
    triagem      = Column(SAEnum(TriagemEnum), default=TriagemEnum.green)
    status       = Column(SAEnum(StatusEnum), default=StatusEnum.internado)
    diagnostico  = Column(String(200))
    medico_resp  = Column(String(120))
    alergias     = Column(String(200))
    comorbidades = Column(String(300))
    anamnese     = Column(Text)
    admissao     = Column(DateTime(timezone=True), server_default=func.now())
    updated_at   = Column(DateTime(timezone=True), onupdate=func.now())
    # Relacionamentos
    vitais       = relationship("VitalSign",  back_populates="patient", cascade="all, delete-orphan")
    medicamentos = relationship("Medication", back_populates="patient", cascade="all, delete-orphan")
    exames       = relationship("Exam",       back_populates="patient", cascade="all, delete-orphan")
    soaps        = relationship("SOAPNote",   back_populates="patient", cascade="all, delete-orphan")
    timeline     = relationship("TimelineEvent", back_populates="patient", cascade="all, delete-orphan")

class VitalSign(Base):
    __tablename__ = "vital_signs"
    id         = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    pa_sistol  = Column(Integer)
    pa_diast   = Column(Integer)
    fc         = Column(Integer)
    temperatura= Column(Float)
    spo2       = Column(Float)
    fr         = Column(Integer)
    glicemia   = Column(Float)
    registered_at = Column(DateTime(timezone=True), server_default=func.now())
    patient    = relationship("Patient", back_populates="vitais")

class Medication(Base):
    __tablename__ = "medications"
    id         = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    nome       = Column(String(120), nullable=False)
    dose       = Column(String(50))
    frequencia = Column(String(50))
    via        = Column(String(30))
    prescrito_em = Column(DateTime(timezone=True), server_default=func.now())
    patient    = relationship("Patient", back_populates="medicamentos")

class Exam(Base):
    __tablename__ = "exams"
    id         = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    nome       = Column(String(120), nullable=False)
    resultado  = Column(String(200))
    status     = Column(String(30), default="Pendente")
    realizado_em = Column(DateTime(timezone=True), server_default=func.now())
    patient    = relationship("Patient", back_populates="exames")

class SOAPNote(Base):
    __tablename__ = "soap_notes"
    id         = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    user_id    = Column(Integer, ForeignKey("users.id"))
    subjetivo  = Column(Text)
    objetivo   = Column(Text)
    avaliacao  = Column(Text)
    plano      = Column(Text)
    gerado_ia  = Column(Integer, default=0)  # 0=manual, 1=ia
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    patient    = relationship("Patient", back_populates="soaps")

class TimelineEvent(Base):
    __tablename__ = "timeline_events"
    id         = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    descricao  = Column(Text, nullable=False)
    tipo       = Column(String(30), default="geral")  # geral, alerta, ia, exame
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    patient    = relationship("Patient", back_populates="timeline")
