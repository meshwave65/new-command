import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq

# Carrega a chave da API da Groq de uma variável de ambiente
groq_api_key = os.getenv("GROQ_API_KEY")

# Inicializa o cliente Groq
if not groq_api_key:
    raise ValueError("A variável de ambiente GROQ_API_KEY não está definida.")
client = Groq(api_key=groq_api_key)

app = FastAPI(
    title="Sofia Condenser API",
    description="API para condensação de texto usando Groq LLM.",
    version="1.0.0"
)

# Configuração CORS - Permitir acesso do frontend Vue
# Em produção, você deve restringir isso ao domínio do seu frontend.
origins = [
    "http://localhost:5173",  # Porta padrão do Vite para desenvolvimento
    "http://localhost:8080",
    "https://sofia-c1t8.onrender.com", # Exemplo de domínio de produção
    "https://new-command.onrender.com", # Exemplo de domínio de produção
    "https://sofia-command.meshwave.com.br", # Exemplo de domínio de produção
    "http://sofia-command.meshwave.com.br", # Exemplo de domínio de produção
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CondenseRequest(BaseModel):
    text: str
    mode: str = "human" # 'human' ou 'llm'

class CondenseResponse(BaseModel):
    condensed_text: str

@app.post("/api/v1/condenser/run", response_model=CondenseResponse)
async def condense_text(request: CondenseRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="O texto para condensar não pode estar vazio.")

    # Escolhe o modelo e o prompt com base no modo de otimização
    if request.mode == "llm":
        model_name = "llama-3.1-8b-versatile" # Modelo otimizado para tarefas de IA
        system_prompt = (
            "Você é um assistente de IA especializado em condensar texto para outras IAs/LLMs. "
            "Seu objetivo é extrair a informação mais densa e relevante, removendo redundâncias, "
            "exemplos desnecessários e floreios, mantendo a precisão e a completude da informação "
            "para que outra IA possa processá-la de forma eficiente. Não adicione introduções, "
            "conclusões ou qualquer texto que não seja a condensação direta do conteúdo fornecido."
        )
    else: # mode == "human"
        model_name = "llama-3.1-8b-versatile" # Modelo otimizado para leitura humana
        system_prompt = (
            "Você é um assistente de IA especializado em condensar texto para leitura humana. "
            "Seu objetivo é resumir o texto de forma concisa, clara e fácil de entender, "
            "mantendo as ideias principais e o contexto. O texto condensado deve ser fluído, "
            "sem jargões desnecessários e com foco na legibilidade. Não adicione introduções, "
            "conclusões ou qualquer texto que não seja a condensação direta do conteúdo fornecido."
        )

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": f"Condense o seguinte texto: {request.text}",
                }
            ],
            model=model_name,
            temperature=0.2, # Baixa temperatura para respostas mais focadas
            max_tokens=min(1024, len(request.text) // 2), # Limita o tamanho da resposta para ser menor que o original
        )
        condensed_text = chat_completion.choices[0].message.content
        return CondenseResponse(condensed_text=condensed_text)
    except Exception as e:
        print(f"Erro ao chamar a API da Groq: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar a condensação: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
