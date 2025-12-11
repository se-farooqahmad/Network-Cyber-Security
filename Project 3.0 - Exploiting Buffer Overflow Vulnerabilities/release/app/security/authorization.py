from fastapi import HTTPException, status, Request
# from fastapi.templating import Jinja2Templates
from app.security.access_ctrl import AccessController
from app.config import TEMPLATE_DIR, ACCESS_CONFIG

# templates = Jinja2Templates(directory=TEMPLATE_DIR)

class AuthorizationManager:
    """Handles user authorization and access control."""

    def __init__(self, config_path: str):
        self.access_ctrl = AccessController(config_path)

    def get_user_role(self, username: str) -> str:
        """Determines the user's role based on their username."""
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

        if username.endswith("_u2"):
            return "bank"
        elif username.endswith("_u3"):
            return "disco"
        else:
            return "customer"

    def check_access(self,request: Request, user: dict):
        """Checks if the user has access to a given endpoint."""
        role = self.get_user_role(user.get("username"))
        
        if not self.access_ctrl.is_allowed(role, request.url.path):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access forbidden"
            )

# Create a global authorization manager instance
authorization_mgr = AuthorizationManager(ACCESS_CONFIG)