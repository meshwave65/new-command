from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# =========================
# APP INIT
# =========================
app = FastAPI(
    title="Sofia Condenser API",
    version="1.0.0"
)

# =========================
# CORS (ESSENCIAL - FIX DO TEU ERRO)
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://condenser.meshwave.com.br"
    ],
    allow_credentials=True,
    allow_methods=["*"],   # inclui OPTIONS (preflight)
    allow_headers=["*"],
)

# =========================
# MODEL
# =========================
class CondenseRequest(BaseModel):
    text: str
    mode: str = "human"

# =========================
# ROUTE PRINCIPAL
# =========================
@app.post("/api/v1/condenser/run")
def condense_text(payload: CondenseRequest):
    
    text = payload.text
    mode = payload.mode

    # 🔥 MOCK SIMPLES (substituir depois por Groq/LLM)
    if mode == "human":
        condensed = text[: max(10, len(text)//2)]
    else:
        condensed = text.replace(" ", "")

    return {
        "condensed_text": condensed
    }

# =========================
# HEALTHCHECK (opcional)
# =========================
@app.get("/health")
def health():
    return {"status": "ok"}
