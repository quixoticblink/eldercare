"""M-CORE · errors a senior may read on their phone.

`detail` stays an English sentence (the coordinator, the logs and the smoke
tests read it). `code` is a short stable id the frontend maps to the person's
language (v1.7). Only errors a caregiver or kaki can actually run into at the
door or at sign-in carry a code; everything else is a plain HTTPException.

    raise KakisError(400, "Wrong code — check and try again", "code_wrong")
    → {"detail": "Wrong code — check and try again", "error": "code_wrong"}
"""
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

class KakisError(HTTPException):
    def __init__(self, status_code: int, detail: str, code: str):
        super().__init__(status_code, detail)
        self.code = code

async def kakis_error_handler(request: Request, exc: KakisError):
    return JSONResponse(status_code=exc.status_code,
                        content={"detail": exc.detail, "error": exc.code})

def install(app):
    app.add_exception_handler(KakisError, kakis_error_handler)
