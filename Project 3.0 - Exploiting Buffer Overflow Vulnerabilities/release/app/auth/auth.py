from fastapi import APIRouter, Request, Depends, HTTPException, status, Cookie
from fastapi.responses import RedirectResponse
import jwt
from app.config import SECRET_KEY, ALGORITHM, SESSION_COOKIE_NAME, HOST_IP, ACTIVE_PROTOCOL
from app.auth.session_manager import session_manager

router = APIRouter()

# Validates the session token, and returns a dictionary containing username. If the token is invalid, raises an exception.
async def validate_session(session_token: str | None = Cookie(default=None)):

    # implementation redacted

    # always returns a dummy user for now
    return {"username": "test_u3",
            "email" : "admin@gmail.com",
            "role"  : "IT officer",
            "name"  : "John Doe",
            "number": "1234567890"}


@router.get("/signout")
async def signout(request: Request, user: dict = Depends(validate_session)):

    # implementation redacted

    raise NotImplementedError