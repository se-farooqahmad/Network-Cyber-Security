from fastapi import FastAPI, Request, UploadFile, File, Form, Depends, HTTPException, status, APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from pathlib import Path
import shutil
import subprocess

from app.auth.auth import validate_session

router = APIRouter()

templates = Jinja2Templates(directory="templates")


def get_user_details(user: dict):
    # user dict contains only email and username from which we can fetch the profile details, but for now we can simply use the user dict as it is coming from validate_session

    return user

@router.get("/picture", response_class=FileResponse)
async def get_picture(user: dict = Depends(validate_session)):
    username = user.get("username")

    # check if the user has uploaded a profile picture
    file_path = Path(f"cache/{username}.bmp")
    if not file_path.exists():
        file_path = Path("static/default.bmp")

    return file_path

@router.get("/profile", response_class=HTMLResponse)
async def get_profile(request: Request, user: dict = Depends(validate_session)):
    return templates.TemplateResponse("profile/profile.html", {"request": request, "user": get_user_details(user)})

@router.post("/profile")
async def post_profile(request: Request, file: UploadFile = File(...), user: dict = Depends(validate_session)):
    
    username = user.get("username")
    
    # save the uploaded file
    file_path = Path(f"cache/{username}.ppm")
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # convert the ppm file to bmp using the converter binary in the bin directory
    # usage of the converter binary: ./converter <input_file> <output_file>
    process = subprocess.run(["bin/converter", file_path, file_path.with_suffix(".bmp")])
    if process.returncode != 0:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error processing the uploaded image")
    
    # redirect back to the dashboard page (make sure its a GET request)
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)