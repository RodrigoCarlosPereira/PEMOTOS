from pydantic import BaseModel

class ChatInput(BaseModel):
    pergunta: str