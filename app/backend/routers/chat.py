"""M-HELP · chatbot endpoint.

The help button is deliberately reachable before sign-in — "how do I sign in?"
is the question a confused caregiver most needs answered, and requiring a token
to ask it was a bug, not a policy.

So the endpoint takes optional auth:
  signed in    → the LLM, with the full app context
  signed out   → the built-in keyword guide only

Signed-out traffic never reaches a paid provider. That keeps an unauthenticated
endpoint from becoming an open bill, and is why this is not simply made public.
"""
from fastapi import APIRouter, Header, Request
from pydantic import BaseModel
from .. import db, security
from ..services import llm, ratelimit

router = APIRouter(prefix="/chat", tags=["help"])

class ChatIn(BaseModel):
    message: str
    history: list[dict] = []

def _optional_user(authorization: str):
    """Resolve a user if a valid token is present; never raise if not."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    uid = security.parse_token(authorization[7:])
    if not uid:
        return None
    return db.one("SELECT * FROM users WHERE id = ?", [uid])

@router.post("")
def chat(body: ChatIn, request: Request = None, authorization: str = Header(default="")):
    user = _optional_user(authorization)
    if user:
        return {"reply": llm.reply(body.message, body.history), "source": "assistant"}

    # Anonymous: keyword guide only, and lightly capped so a script cannot sit
    # on the endpoint. The cap is generous — a real person asking a few
    # questions from the sign-in screen will never see it.
    ip = ratelimit.client_ip(request)
    if ip and ratelimit.count("chat_anon", ip, 15) > 60:
        return {"reply": ("刚才回答了很多问题。请登录，或致电巴西立 ICCP 协调员 6XXX XXXX。"
                          if llm.is_zh(body.message) else
                          "I've answered a lot of questions just now. Please sign in, "
                          "or call the Pasir Ris ICCP coordinator on 6XXX XXXX."),
                "source": "throttled"}
    if ip:
        ratelimit.record("chat_anon", ip)
    return {"reply": llm.guide_reply(body.message), "source": "guide"}
