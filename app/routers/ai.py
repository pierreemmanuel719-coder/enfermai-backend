from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User, TimelineEvent
from app.schemas import AIRequest, AIResponse
from app.auth import get_current_user
from app.config import settings
import httpx

router = APIRouter()

CLAUDE_URL = "https://api.anthropic.com/v1/messages"

def _claude_headers():
    return {
        "x-api-key": settings.ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

@router.post("/analisar", response_model=AIResponse)
async def analisar(
    body: AIRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not settings.ANTHROPIC_API_KEY:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY não configurada no servidor")

    payload = {
        "model": settings.CLAUDE_MODEL,
        "max_tokens": 1000,
        "system": (
            "Você é um assistente clínico de apoio à enfermagem. "
            "Analise o quadro e forneça: 3 hipóteses diagnósticas com probabilidade, "
            "principais diagnósticos de enfermagem (NANDA), prioridades de cuidado, "
            "exames recomendados. Responda em português, de forma objetiva e estruturada."
        ),
        "messages": [{"role": "user", "content": body.prompt}],
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(CLAUDE_URL, json=payload, headers=_claude_headers())

    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Erro na API Claude: {resp.text}")

    data = resp.json()
    text = "".join(c.get("text", "") for c in data.get("content", []))
    return {"resultado": text}


@router.post("/gerar-soap")
async def gerar_soap(
    body: AIRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Gera evolução SOAP a partir do quadro clínico descrito."""
    if not settings.ANTHROPIC_API_KEY:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY não configurada no servidor")

    payload = {
        "model": settings.CLAUDE_MODEL,
        "max_tokens": 800,
        "system": (
            "Você é enfermeiro especialista. Gere uma evolução SOAP em português. "
            'Responda APENAS com JSON no formato: {"S":"...","O":"...","A":"...","P":"..."}'
        ),
        "messages": [{"role": "user", "content": body.prompt}],
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(CLAUDE_URL, json=payload, headers=_claude_headers())

    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Erro na API Claude: {resp.text}")

    data = resp.json()
    text = "".join(c.get("text", "") for c in data.get("content", []))
    # Limpar possíveis backticks de markdown
    clean = text.replace("```json", "").replace("```", "").strip()

    try:
        import json
        parsed = json.loads(clean)
    except Exception:
        raise HTTPException(status_code=502, detail="Resposta da IA não pôde ser interpretada")

    return parsed
