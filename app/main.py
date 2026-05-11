from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, patients, ai, soap
from app.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="EnferMAI API",
    description="Backend clínico para o sistema EnferMAI 2.0",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique o domínio do frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,     prefix="/api/auth",     tags=["Autenticação"])
app.include_router(patients.router, prefix="/api/patients", tags=["Pacientes"])
app.include_router(ai.router,       prefix="/api/ai",       tags=["IA Clínica"])
app.include_router(soap.router,     prefix="/api/soap",     tags=["Evolução SOAP"])

@app.get("/")
def root():
    return {"status": "ok", "app": "EnferMAI API v1.0"}

@app.get("/health")
def health():
    return {"status": "healthy"}
