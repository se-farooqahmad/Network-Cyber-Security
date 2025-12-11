from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import RedirectResponse
import requests
import jwt
from app.config import AUTH_SERVER_IP, CLIENT_ID, CLIENT_SECRET, SECRET_KEY, ALGORITHM, SESSION_COOKIE_NAME, HOST_IP, SESSION_DURATION, ACTIVE_PROTOCOL
from app.auth.session_manager import session_manager

router = APIRouter()

# The default callback endpoint for the OAuth2 flow. This endpoint is called by the auth server after the user authenticates and authorizes the client application.
@router.post("/callback")
async def getAccessToken(request: Request, code: str):

    # implementation redacted

    raise NotImplementedError
