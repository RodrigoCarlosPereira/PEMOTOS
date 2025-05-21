from dotenv import load_dotenv
from fastapi import FastAPI, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import StreamingResponse
from openai import OpenAI
from io import BytesIO
import sqlite3
import openai
import os
import secrets
import pandas as pd

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


class ChatInput(BaseModel):
    pergunta: str


# Página inicial (chat)
@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open(os.path.join("static", "index.html"), "r", encoding="utf-8") as file:
        return file.read()


# Endpoint do chat
@app.post("/chat")
async def chat_pergunta(body: ChatInput):
    pergunta_lower = body.pergunta.lower().strip()

    # Detecção de intenção de simulação
    if "quero simular" in pergunta_lower or "simular" in pergunta_lower:
        conn = sqlite3.connect("motos.db")
        cursor = conn.cursor()
        cursor.execute('SELECT nome, link_simulacao FROM motos')
        motos_data = cursor.fetchall()
        conn.close()

        resposta = "Certo! Qual dessas motos você deseja simular?<br><br>"
        for nome, link in motos_data:
            resposta += f"""
            <div style="margin-bottom: 10px;">
              <strong>{nome}</strong><br>
              <a href="{link}" target="_blank" style="display: inline-block; padding: 6px 12px; background: #cc0000; color: white; text-decoration: none; border-radius: 4px;">Simular</a>
            </div>
            """

        # Registrar pergunta/resposta
        conn = sqlite3.connect("motos.db")
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historico_perguntas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pergunta TEXT NOT NULL,
                resposta TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute(
            "INSERT INTO historico_perguntas (pergunta, resposta) VALUES (?, ?)",
            (body.pergunta, resposta)
        )
        conn.commit()
        conn.close()

        return JSONResponse(content={"resposta": resposta})

    # Chamada à OpenAI para perguntas gerais
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": """
                    Você é um atendente especializado em consórcios da Pernambuco Motos (Pe Motos). Seu objetivo é fornecer respostas claras, objetivas e precisas, sem enrolação, sempre levando em consideração os regulamentos e as condições dos consórcios de aquisição de produtos da Honda, como motos e outros veículos. 

                    Suas respostas devem ser baseadas nos seguintes pontos principais:
                    1. **Clareza nas condições**: Explique detalhadamente as condições do consórcio, como prazos, taxas de administração, contemplação, e valores de parcelas, sem usar jargões ou termos complicados.
                    2. **Compreensão das regras**: Certifique-se de que o cliente compreenda como o consórcio funciona, destacando aspectos como o sorteio, a carta de crédito, e os custos adicionais, como taxas de adesão e custos financeiros.
                    3. **Objetividade**: Respostas diretas, evitando informações desnecessárias ou evasivas. Lembre-se de que a transparência é essencial no atendimento.
                    4. **Flexibilidade**: Informe o cliente sobre as diferentes opções de planos de consórcio, prazos e valores que podem ser adaptados de acordo com o perfil do cliente, sempre alinhando a solução ao seu perfil financeiro.
                    5. **Atendimento ao cliente**: Sempre se mostre disponível para esclarecer dúvidas adicionais e nunca deixe de fazer o cliente se sentir confortável e bem atendido.

                    Se a questão não for clara o suficiente, pergunte de maneira cortês e objetiva para entender melhor o que o cliente deseja saber.
                 """},

                {"role": "user", "content": body.pergunta}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        resposta = response['choices'][0]['message']['content'].strip()

        # Registrar pergunta/resposta
        conn = sqlite3.connect("motos.db")
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historico_perguntas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pergunta TEXT NOT NULL,
                resposta TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute(
            "INSERT INTO historico_perguntas (pergunta, resposta) VALUES (?, ?)",
            (body.pergunta, resposta)
        )
        conn.commit()
        conn.close()

        return JSONResponse(content={"resposta": resposta})
    except Exception as e:
        print("Erro:", e)
        return JSONResponse(content={"resposta": "Desculpe, houve um erro ao tentar responder. Tente novamente mais tarde."})


# Registrar acesso ao chat
@app.post("/registrar-acesso", status_code=status.HTTP_204_NO_CONTENT)
async def registrar_acesso():
    try:
        conn = sqlite3.connect("motos.db")
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS acessos_chat (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute("INSERT INTO acessos_chat DEFAULT VALUES")
        conn.commit()
        conn.close()
    except Exception as e:
        print("Erro ao registrar acesso:", e)


# Retornar motos para simulação
@app.get("/motos")
async def get_motos():
    conn = sqlite3.connect("motos.db")
    cursor = conn.cursor()

    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS motos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            link_simulacao TEXT NOT NULL
        )
    ''')
    cursor.execute('DELETE FROM motos')
    cursor.execute(''' 
        INSERT OR IGNORE INTO motos (nome, link_simulacao) VALUES
        ('POP 110i', 'https://consorcio.pernambucomotos.com.br/products/pop-110i'),
        ('CG 160 START', 'https://consorcio.pernambucomotos.com.br/products/cg-160-start'),
        ('BIZ 125 ES', 'https://consorcio.pernambucomotos.com.br/products/biz-125-es'),
        ('PCX', 'https://consorcio.pernambucomotos.com.br/products/pcx');
    ''')
    conn.commit()

    cursor.execute('SELECT nome, link_simulacao FROM motos')
    motos_data = cursor.fetchall()
    conn.close()

    motos = [{"nome": nome, "link_simulacao": link} for nome, link in motos_data]
    return JSONResponse(content=motos)


# Ver total de acessos
@app.get("/admin/acessos")
async def contar_acessos():
    conn = sqlite3.connect("motos.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS acessos_chat (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute("SELECT COUNT(*) FROM acessos_chat")
    total = cursor.fetchone()[0]
    conn.close()
    return {"total_acessos": total}


# Ver histórico de perguntas
@app.get("/admin/perguntas")
async def listar_perguntas():
    conn = sqlite3.connect("motos.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historico_perguntas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pergunta TEXT NOT NULL,
            resposta TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute("SELECT pergunta, resposta, timestamp FROM historico_perguntas ORDER BY timestamp DESC")
    historico = cursor.fetchall()
    conn.close()

    return JSONResponse(content=[
        {"pergunta": p, "resposta": r, "timestamp": t}
        for p, r, t in historico
    ])


# Autenticação básica para acesso ao painel admin
security = HTTPBasic()

def autenticar(credentials: HTTPBasicCredentials = Depends(security)):
    usuario_correto = secrets.compare_digest(credentials.username, "PEadmin")
    senha_correta = secrets.compare_digest(credentials.password, "@PernaB243567")
    if not (usuario_correto and senha_correta):
        raise HTTPException(
            status_code=401,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Basic"}
        )
    return credentials.username


@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(user: str = Depends(autenticar)):
    with open(os.path.join("static", "admin.html"), "r", encoding="utf-8") as f:
        return f.read()


# Endpoint para exportar acessos para Excel
# Endpoint para exportar acessos para Excel com autenticação
@app.get("/admin/exportar-acessos")
async def exportar_acessos(user: str = Depends(autenticar)):
    conn = sqlite3.connect("motos.db")
    cursor = conn.cursor()
    cursor.execute('''SELECT id, timestamp FROM acessos_chat ORDER BY timestamp DESC''')
    acessos = cursor.fetchall()
    conn.close()

    # Criar um DataFrame com os dados
    df_acessos = pd.DataFrame(acessos, columns=["ID", "Timestamp"])

    # Gerar o arquivo Excel em memória
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_acessos.to_excel(writer, index=False, sheet_name="Acessos")

    output.seek(0)
    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=acessos.xlsx"})


# Endpoint para exportar histórico de perguntas para Excel com autenticação
@app.get("/admin/exportar-perguntas")
async def exportar_perguntas(user: str = Depends(autenticar)):
    conn = sqlite3.connect("motos.db")
    cursor = conn.cursor()
    cursor.execute('''SELECT pergunta, resposta, timestamp FROM historico_perguntas ORDER BY timestamp DESC''')
    perguntas = cursor.fetchall()
    conn.close()

    # Criar um DataFrame com os dados
    df_perguntas = pd.DataFrame(perguntas, columns=["Pergunta", "Resposta", "Timestamp"])

    # Gerar o arquivo Excel em memória
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_perguntas.to_excel(writer, index=False, sheet_name="Perguntas")

    output.seek(0)
    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=perguntas.xlsx"})
