"""M-HELP · chatbot endpoint."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from .. import security
from ..services import llm

router = APIRouter(prefix="/chat", tags=["help"])

class ChatIn(BaseModel):
    message: str
    history: list[dict] = []

@router.post("")
def chat(body: ChatIn, user=Depends(security.current_user)):
    return {"reply": llm.reply(body.message, body.history)}
