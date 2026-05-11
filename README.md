# EnferMAI 2.0 — Backend

Backend FastAPI + PostgreSQL para o sistema EnferMAI 2.0.

---

## 📁 Estrutura

```
enfermai-backend/
├── app/
│   ├── main.py          # Entry point FastAPI
│   ├── database.py      # Conexão PostgreSQL
│   ├── config.py        # Variáveis de ambiente
│   ├── auth.py          # JWT + bcrypt
│   ├── schemas.py       # Pydantic models
│   ├── models/
│   │   └── models.py    # SQLAlchemy models
│   └── routers/
│       ├── auth.py      # POST /api/auth/login|register
│       ├── patients.py  # CRUD pacientes + vitais/meds/exames/timeline
│       ├── ai.py        # Proxy seguro → Claude API
│       └── soap.py      # CRUD evoluções SOAP
├── requirements.txt
├── Procfile
├── railway.toml
└── .env.example
```

---

## 🚀 Deploy no Railway (Recomendado — Gratuito)

### 1. Criar conta
Acesse https://railway.app e crie conta com GitHub.

### 2. Criar projeto
- Clique **New Project → Deploy from GitHub repo**
- Selecione este repositório (ou faça upload da pasta)

### 3. Adicionar PostgreSQL
- No projeto Railway, clique **+ New → Database → PostgreSQL**
- Railway cria o banco automaticamente

### 4. Configurar variáveis de ambiente
No painel do projeto Railway, vá em **Variables** e adicione:

| Variável | Valor |
|---|---|
| `DATABASE_URL` | (Railway preenche automaticamente via `${{Postgres.DATABASE_URL}}`) |
| `SECRET_KEY` | Uma string aleatória longa (ex: `openssl rand -hex 32`) |
| `ANTHROPIC_API_KEY` | Sua key em https://console.anthropic.com |

### 5. Deploy automático
Railway detecta o `Procfile` e faz o deploy automaticamente.

**URL do backend:** `https://enfermai-backend-production.up.railway.app`

---

## 🚀 Deploy no Render (Alternativa Gratuita)

1. Acesse https://render.com e crie conta
2. **New → Web Service → Connect Repository**
3. Configurações:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Em **Environment Variables**, adicione as mesmas variáveis acima
5. **New → PostgreSQL** para criar o banco

---

## 💻 Rodar Localmente

```bash
# 1. Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Configurar variáveis
cp .env.example .env
# Edite o .env com suas credenciais

# 4. Rodar
uvicorn app.main:app --reload
```

Acesse: http://localhost:8000/docs (Swagger UI automático)

---

## 🔗 Conectar o Frontend

No arquivo `enfermai_com_backend.html`, altere a linha:

```javascript
const API_BASE = 'https://SEU-BACKEND.railway.app';
```

Para a URL real do seu backend. Exemplo:

```javascript
const API_BASE = 'https://enfermai-backend-production.up.railway.app';
```

---

## 📡 Endpoints Principais

### Auth
| Método | Rota | Descrição |
|---|---|---|
| POST | `/api/auth/register` | Cadastrar enfermeiro |
| POST | `/api/auth/login` | Login → retorna JWT |
| GET | `/api/auth/me` | Perfil do usuário logado |

### Pacientes
| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/patients/` | Listar todos |
| POST | `/api/patients/` | Novo paciente |
| GET | `/api/patients/{id}` | Detalhes + vitais/meds/exames |
| PATCH | `/api/patients/{id}` | Atualizar |
| DELETE | `/api/patients/{id}` | Remover |
| POST | `/api/patients/{id}/vitais` | Registrar sinais vitais |
| POST | `/api/patients/{id}/meds` | Adicionar medicamento |
| POST | `/api/patients/{id}/exames` | Adicionar exame |
| GET | `/api/patients/{id}/timeline` | Linha do tempo |
| POST | `/api/patients/{id}/timeline` | Adicionar evento |

### IA Clínica
| Método | Rota | Descrição |
|---|---|---|
| POST | `/api/ai/analisar` | Análise clínica com Claude |
| POST | `/api/ai/gerar-soap` | Gerar SOAP com IA |

### SOAP
| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/soap/{patient_id}` | Listar evoluções |
| POST | `/api/soap/{patient_id}` | Salvar evolução |

---

## 🔒 Segurança

- API Key do Claude **nunca exposta** no frontend
- Autenticação JWT com expiração de 12 horas
- Senhas com bcrypt
- CORS configurável por domínio em produção

---

## 📦 Primeiro Uso

Após o deploy, registre o primeiro usuário via Swagger (`/docs`) ou curl:

```bash
curl -X POST https://SEU-BACKEND.railway.app/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"nome":"Ana Beatriz","email":"ana@hospital.com","password":"suasenha","coren":"SP-456789","funcao":"Enfermeira","setor":"UTI Cardiológica"}'
```
