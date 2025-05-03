from fastapi import APIRouter
from src.routers.chat import router as chatRouter


router = APIRouter()

router.include_router(chatRouter, prefix="/chat", tags=["Chat"])

