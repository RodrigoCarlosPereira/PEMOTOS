from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import sqlite3
import openai
import os

load_dotenv()
print("API KEY:", os.getenv("OPENAI_API_KEY"))

openai.api_key = os.getenv("OPENAI_API_KEY")


# Verificação da chave da API (depuração)
if not openai.api_key:
    print("Chave da API não configurada!")
else:
    print("Chave da API carregada com sucesso.")

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

class ChatInput(BaseModel):
    pergunta: str

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open(os.path.join("static", "index.html"), "r", encoding="utf-8") as file:
        return file.read()

@app.post("/chat")
async def chat_pergunta(body: ChatInput):
    pergunta_lower = body.pergunta.lower().strip()

    # Detecta intenção de simulação
    if "quero simular" in pergunta_lower or "simular" in pergunta_lower:
        conn = sqlite3.connect("motos.db")
        cursor = conn.cursor()
        cursor.execute('SELECT nome, link_simulacao FROM motos')
        motos_data = cursor.fetchall()
        conn.close()

        # Gera HTML com botões
        resposta = "Certo! Qual dessas motos você deseja simular?<br><br>"
        for nome, link in motos_data:
            resposta += f"""
            <div style="margin-bottom: 10px;">
              <strong>{nome}</strong><br>
              <a href="{link}" target="_blank" style="display: inline-block; padding: 6px 12px; background: #cc0000; color: white; text-decoration: none; border-radius: 4px;">Simular</a>
            </div>
            """

        return JSONResponse(content={"resposta": resposta})

    # Caso contrário, usar a OpenAI para responder normalmente
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um atendente especializado em consórcios da Pernambuco Motos."},
                {"role": "user", "content": body.pergunta}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        resposta = response['choices'][0]['message']['content'].strip()
        return JSONResponse(content={"resposta": resposta})
    except Exception as e:
        print("Erro:", e)
        return JSONResponse(content={"resposta": "Desculpe, houve um erro ao tentar responder. Tente novamente mais tarde."})
@app.get("/motos")
async def get_motos():
    conn = sqlite3.connect("motos.db")
    cursor = conn.cursor()

    # Criação da tabela caso ela não exista
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS motos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            link_simulacao TEXT NOT NULL
        )
    ''')

    # Limpando e inserindo dados na tabela
    cursor.execute('DELETE FROM motos')
    cursor.execute(''' 
        INSERT OR IGNORE INTO motos (nome, link_simulacao) VALUES
        ('POP 110i', 'https://consorcio.pernambucomotos.com.br/products/pop-110i'),
        ('CG 160 START', 'https://consorcio.pernambucomotos.com.br/products/cg-160-start'),
        ('BIZ 125 ES', 'https://consorcio.pernambucomotos.com.br/products/biz-125-es'),
        ('PCX', 'https://consorcio.pernambucomotos.com.br/products/pcx');
    ''')
    conn.commit()

    # Recuperando as motos do banco de dados
    cursor.execute('SELECT nome, link_simulacao FROM motos')
    motos_data = cursor.fetchall()
    print("Motos do banco de dados:", motos_data)  # Para depuração
    conn.close()

    motos = [{"nome": nome, "link_simulacao": link} for nome, link in motos_data]
    return JSONResponse(content=motos)
