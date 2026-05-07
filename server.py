import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv
load_dotenv(dotenv_path="../.env")

# ==================================================
# GROQ KEY
# ==================================================
groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    raise ValueError("A variável de ambiente GROQ_API_KEY não está definida.")

client = Groq(api_key=groq_api_key)

# ==================================================
# APP
# ==================================================
app = FastAPI(
    title="Sofia Condenser API",
    description="API para condensação de texto usando Groq LLM.",
    version="1.0.0"
)

# ==================================================
# CORS (SÓ CORREÇÃO REAL NECESSÁRIA)
# ==================================================
origins = [
    "http://localhost:5173",
    "http://localhost:8080",
    "https://sofia-c1t8.onrender.com",
    "https://new-command.onrender.com",
    "https://sofia-command.meshwave.com.br",
    "http://sofia-command.meshwave.com.br",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,   # FIX REAL DO PREFLIGHT
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# ==================================================
# MODELS
# ==================================================
class CondenseRequest(BaseModel):
    text: str
    mode: str = "human"

class CondenseResponse(BaseModel):
    condensed_text: str

# ==================================================
# ENDPOINT
# ==================================================
@app.post("/api/v1/condenser/run", response_model=CondenseResponse)
async def condense_text(request: CondenseRequest):

    if not request.text.strip():
        raise HTTPException(
            status_code=400,
            detail="O texto para condensar não pode estar vazio."
        )

    # ==================================================
    # ESCOLHA DE MODELO + PROMPT (INTACTO - NÃO MEXIDO)
    # ==================================================
    if request.mode == "llm":
        model_name = "llama-3.1-8b-versatile"
        system_prompt = (
            "Você é um assistente de IA especializado em condensar texto para outras IAs/LLMs. "
            "Seu objetivo é extrair a informação mais densa e relevante, removendo redundâncias, "
            "exemplos desnecessários e floreios, mantendo a precisão e a completude da informação "
            "para que outra IA possa processá-la de forma eficiente. Não adicione introduções, "
            "conclusões ou qualquer texto que não seja a condensação direta do conteúdo fornecido."
        )
    else:
        model_name = "llama-3.1-8b-versatile"
        system_prompt = (
            "Você é um assistente de IA especializado em condensar texto para leitura humana. "
            "Seu objetivo é resumir o texto de forma concisa, clara e fácil de entender, "
            "mantendo as ideias principais e o contexto. O texto condensado deve ser fluído, "
            "sem jargões desnecessários e com foco na legibilidade. Não adicione introduções, "
            "conclusões ou qualquer texto que não seja a condensação direta do conteúdo fornecido."
        )

    try:
        chat_completion = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.text},
            ],
            temperature=0.2,

            # FIX REAL (EVITA max_tokens=0)
            max_tokens=max(64, min(1024, len(request.text) // 2)),
        )

        return CondenseResponse(
            condensed_text=chat_completion.choices[0].message.content
        )

    except Exception as e:
        print("Erro Groq:", e)
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar condensação: {str(e)}"
        )

# ==================================================
# RUN
# ==================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
