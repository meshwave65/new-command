import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(dotenv_path=os.path.join(BASE_DIR, "../.env"))oq import Groq

# ==================================================
# GROQ KEY
# ==================================================
groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    raise ValueError("GROQ_API_KEY não definida no ambiente")

print("\n==============================")
print("DEBUG GROQ API KEY")
print("VALUE:", groq_api_key)
print("LENGTH:", len(groq_api_key))
print("==============================\n")

client = Groq(api_key=groq_api_key)

# ==================================================
# FASTAPI
# ==================================================
app = FastAPI(
    title="Sofia Condenser API",
    version="1.0.0"
)

# ==================================================
# CORS
# ==================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5177",
        "http://localhost:5173",
        "https://condenser.meshwave.com.br"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# ==================================================
# MODEL
# ==================================================
class CondenseRequest(BaseModel):
    text: str
    mode: str = "human"

# ==================================================
# ENDPOINT
# ==================================================
@app.post("/api/v1/condenser/run")
async def condense_text(request: CondenseRequest):

    if not request.text or not request.text.strip():
        return {
            "condensed_text": "Texto vazio recebido."
        }

    # ==================================================
    # ESCOLHA DE MODELO + PROMPT (INTACTO - NÃO MEXIDO)
    # ==================================================
    if request.mode == "llm":
        model_name = "llama-3.1-8b-instant"
        system_prompt = (
            "Você é um assistente de IA especializado em condensar texto para outras IAs/LLMs. "
            "Seu objetivo é extrair a informação mais densa e relevante, removendo redundâncias, "
            "exemplos desnecessários e floreios, mantendo a precisão e a completude da informação "
            "para que outra IA possa processá-la de forma eficiente. Não adicione introduções, "
            "conclusões ou qualquer texto que não seja a condensação direta do conteúdo fornecido."
        )
    else:
        model_name = "llama-3.3-70b-versatile"
        system_prompt = (
            "Você é um assistente de IA especializado em condensar texto para leitura humana. "
            "Seu objetivo é resumir o texto de forma concisa, clara e fácil de entender, "
            "mantendo as ideias principais e o contexto. O texto condensado deve ser fluído, "
            "sem jargões desnecessários e com foco na legibilidade. Não adicione introduções, "
            "conclusões ou qualquer texto que não seja a condensação direta do conteúdo fornecido."
        )

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": f"Condense o seguinte texto:\n\n{request.text}"
                }
            ],
            temperature=0.2,
            max_tokens=1024
        )

        return {
            "condensed_text": response.choices[0].message.content
        }

    except Exception as e:
        print("ERRO GROQ:", str(e))
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# ==================================================
# HEALTH CHECK
# ==================================================
@app.get("/health")
def health():
    return {"status": "ok"}

# ==================================================
# RUN LOCAL
# ==================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
