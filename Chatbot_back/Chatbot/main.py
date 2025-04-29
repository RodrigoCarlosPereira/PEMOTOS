from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import sqlite3
import os

app = FastAPI()

# Montar a pasta estática para servir o HTML direto
app.mount("/static", StaticFiles(directory="static"), name="static")


# Página principal
@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open(os.path.join("static", "index.html"), "r", encoding="utf-8") as file:
        return file.read()

# Endpoint para perguntas sobre o consórcio
@app.get("/pergunta/{pergunta}", response_class=HTMLResponse)
async def get_resposta(pergunta: str):
    perguntas_respostas = {
        "Como funciona o consórcio?": "O consórcio é uma modalidade de compra baseada em autofinanciamento, onde participantes contribuem com parcelas mensais até serem contemplados.",
        "Como é feito o consórcio?": "O consórcio é formado por um grupo de pessoas que contribuem mensalmente até que todos recebam uma carta de crédito.",
        "Quais são as vantagens do consórcio?": "Não tem juros, tem prazos flexíveis e você escolhe o valor da sua cota conforme seu planejamento.",
        "O que é o consórcio da Pernambuco Motos?": "É uma modalidade de autofinanciamento que permite adquirir uma moto Honda nova por meio de parcelas mensais.",
        "Quais modelos de motos estão disponíveis?": "A Pernambuco Motos oferece diversos modelos como POP 110i, CG 160 START, BIZ 125 ES, PCX 150, entre outros.",
        "Como posso ser contemplado rapidamente?": "Existem duas formas de contemplação: sorteio e lance. Participar de grupos já em andamento e oferecer lances pode aumentar as chances.",
        "Posso mudar o modelo da moto durante o consórcio?": "Sim, é possível alterar o modelo da moto durante a vigência do consórcio, desde que respeitadas as condições estabelecidas.",
        "Como faço para pagar as parcelas?": "As parcelas podem ser pagas por meio de boletos bancários, que podem ser emitidos pelo aplicativo ou site do Consórcio Nacional Honda.",
        "Posso pagar duas parcelas no mesmo mês?": "Sim, você pode pagar duas parcelas no mesmo mês, e o abatimento ocorrerá a partir da última parcela.",
        "Quais são as taxas envolvidas?": "O consórcio possui uma taxa de administração, que varia conforme o grupo e o plano escolhido.",
        "O que acontece se eu atrasar o pagamento das parcelas?": "Após o acúmulo de quatro parcelas em atraso, a cota será cancelada automaticamente, mas é possível negociar os pagamentos.",
        "Como posso acompanhar o andamento do meu consórcio?": "Você pode acompanhar o andamento do seu consórcio através do aplicativo 'Honda Serviços Financeiros' ou acessando a área 'Meu Consórcio' no site oficial.",
        "Quais são os canais de atendimento da Pernambuco Motos?": "Você pode entrar em contato pelo WhatsApp (81) 98746-603, Instagram @pernambucomotos, ou pelo e-mail contato@pernambucomotos.com.br."
    }

    resposta = perguntas_respostas.get(pergunta, "Desculpe, não entendi a sua pergunta. Tente novamente.")
    return resposta

# Endpoint para fornecer as motos usando o banco de dados
@app.get("/motos")
async def get_motos():
    conn = sqlite3.connect("motos.db")
    cursor = conn.cursor()
    cursor.execute('DELETE FROM motos')

    # Garante que a tabela existe
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS motos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            link_simulacao TEXT NOT NULL
        )
    ''')

    # Inserir algumas motos no banco (caso ainda não existam)
    cursor.execute('''
        INSERT OR IGNORE INTO motos (nome, link_simulacao) VALUES
        ('POP 110i', 'https://consorcio.pernambucomotos.com.br/products/pop-110i'),
        ('CG 160 START', 'https://consorcio.pernambucomotos.com.br/products/cg-160-start'),
        ('BIZ 125 ES', 'https://consorcio.pernambucomotos.com.br/products/biz-125-es'),
        ('PCX', 'https://consorcio.pernambucomotos.com.br/products/pcx');
    ''')

    conn.commit()
    conn.close()

    # Buscar as motos no banco
    conn = sqlite3.connect("motos.db")
    cursor = conn.cursor()
    cursor.execute('SELECT nome, link_simulacao FROM motos')
    motos_data = cursor.fetchall()
    conn.close()

    # Montar a resposta
    motos = [{"nome": nome, "link_simulacao": link} for nome, link in motos_data]
    return JSONResponse(content=motos)
