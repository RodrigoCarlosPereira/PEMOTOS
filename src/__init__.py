from .models.chatInput import ChatInput
from .prompt import Prompt
import os
from dotenv import load_dotenv

# Carregamento do .env
load_dotenv()

# Configuração da API OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Mensagem de depuração
if not OPENAI_API_KEY:
    print("❌ Chave da API não configurada!")
else:
    print("✅ Chave da API carregada com sucesso.")