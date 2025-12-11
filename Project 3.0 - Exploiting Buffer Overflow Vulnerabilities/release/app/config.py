import os
import datetime

ORACLE_HOME = os.environ.get("ORACLE_HOME")

DB_USERNAME = os.environ.get("DB_USERNAME")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_ALIAS = os.environ.get("DB_ALIAS")

OAUTH_REDIRECT_URI = "/callback"
SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")

# OAuth client config. Note that these are the secrets and the ids registered with the OAuth server.
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
CLIENT_ID = os.environ.get("CLIENT_ID")

# session cookie config
SESSION_COOKIE_NAME = "session_token"
SESSION_DURATION = datetime.timedelta(minutes=15)
INTERNAL_SESSION_EXPIRY = datetime.timedelta(minutes=30)

# will be used for communication
AUTH_SERVER_IP = os.environ.get("AUTH_SERVER_IP")
HOST_IP = os.environ.get("HOST_IP")

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
ACCESS_CONFIG = os.path.join(os.path.dirname(__file__), "access.cfg")

ACTIVE_PROTOCOL = "https"