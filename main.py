import os
from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import requests
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")

headers = {"Authorization": API_KEY}

templates = Jinja2Templates(directory="templates")

async def query(filename):
    try:
        with open(filename, "rb") as f:
            data = f.read()
        response = requests.post(API_URL, headers=headers, data=data)
        response.raise_for_status()
        return response.json()
    except (FileNotFoundError, requests.RequestException) as e:
        print(f"Error: {e}")
        return None

app = FastAPI()

app.mount("/temp", StaticFiles(directory="temp"), name="temp")

@app.get("/", response_class=HTMLResponse)
async def first_api(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "output": None})

@app.post("/upload", response_class=HTMLResponse)
async def upload_image(request: Request, file: UploadFile = File(...)):
    os.makedirs("temp", exist_ok=True)

    file_location = f"temp/{file.filename}"
    with open(file_location, "wb") as f:
        f.write(await file.read())
    
    output = await query(file_location)
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "output": output,
        "image_path": file_location
    })