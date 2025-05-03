from src.models.chatInput import ChatInput
from src.prompt import Prompt

router = APIRouter()

@router.post("/chat")
async def chat_pergunta(body: ChatInput):

    try:
        response = Prompt.prompt(body)['choices'][0]['message']['content'].strip()
        
        resposta = response
        print("Resposta da OpenAI:", resposta)  # Para depuração
        return JSONResponse(content={"resposta": resposta})
    except Exception as e:
        print("Erro:", e)  # Para depuração
        return JSONResponse(content={"resposta": "Desculpe, houve um erro ao tentar responder. Tente novamente mais tarde."})