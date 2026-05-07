from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ==================================================
# APP INIT
# ==================================================
app = FastAPI(
    title="Sofia Condenser API",
    version="1.0.0"
)

# ==================================================
# CORS CONFIG (CORREÇÃO DO ERRO ATUAL)
# ==================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://condenser.meshwave.com.br",
        "http://localhost:5173",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],   # inclui GET, POST, OPTIONS (preflight)
    allow_headers=["*"],
)

# ==================================================
# REQUEST MODEL
# ==================================================
class CondenseRequest(BaseModel):
    text: str
    mode: str = "human"

# ==================================================
# CONDENSER ENDPOINT
# ==================================================
@app.post("/api/v1/condenser/run")
def condense_text(payload: CondenseRequest):

    text = payload.text.strip()
    mode = payload.mode

    if not text:
        return {
            "condensed_text": ""
        }

    # ==================================================
    # MOCK LOGIC (substituir por Groq/LLM depois)
    # ==================================================
    if mode == "human":
        # resumo simples humano
        words = text.split()
        condensed = " ".join(words[: max(3, len(words)//2)])

    else:
        # modo LLM / compacto extremo
        condensed = text.replace(" ", "")

    return {
        "condensed_text": condensed
    }

# ==================================================
# HEALTH CHECK
# ==================================================
@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "sofia-condenser-api"
    }
