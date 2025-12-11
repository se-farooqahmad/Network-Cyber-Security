from fastapi import APIRouter, Request, Depends, HTTPException, status, Cookie
from fastapi.responses import HTMLResponse
from app.config import HOST_IP, AUTH_SERVER_IP, CLIENT_ID, OAUTH_REDIRECT_URI, TEMPLATE_DIR, ACTIVE_PROTOCOL
from app.auth.auth import validate_session
from app.security.authorization import authorization_mgr
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory=TEMPLATE_DIR)

# These endpoints are accessible to all users, irrespective of their roles and the authentication status.
@router.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse("home/index.html", {"request": request, "auth_server": AUTH_SERVER_IP, "client_id": CLIENT_ID, "redirect_uri": f"{ACTIVE_PROTOCOL}://{HOST_IP}{OAUTH_REDIRECT_URI}"})

# dashboard is accessible to all authenticated users. we dont need to however change dashboard according to the user role, as it is a generic page.
@router.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard(request: Request, user: dict = Depends(validate_session)):

    authorization_mgr.check_access(request, user)
    return templates.TemplateResponse("home/dashboard.html", {"request": request})