from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.auth import auth, oauth
from app.api import home, payment, retrieval, adjustment, profile

# App server config
app = FastAPI()
origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router)
app.include_router(oauth.router)
app.include_router(home.router)
app.include_router(payment.router)
app.include_router(retrieval.router)
app.include_router(adjustment.router)
app.include_router(profile.router)