from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .database import get_db
from .config import settings

app = FastAPI(title="Smart Email Manager")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/")
async def root():
    return {"message": "Welcome to Smart Email Manager"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
