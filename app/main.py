import os
from fastapi import FastAPI, Depends, HTTPException, Request
# Allow HTTP for local development
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
import secrets

from .database import get_db, Base, engine
from .config import settings
from .models import User
from .services.gmail import GmailService

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Email Manager")
# Add session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=secrets.token_urlsafe(32),  # Generate a random secret key
    session_cookie="session"
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Store state tokens temporarily (in production, use Redis or similar)
state_tokens = {}

@app.get("/")
async def root(request: Request, db: Session = Depends(get_db)):
    # If user is not logged in, redirect to login
    if "user_id" not in request.session:
        return RedirectResponse(url="/login", status_code=303)
    
    user = db.query(User).filter(User.id == request.session["user_id"]).first()
    emails = []
    
    if user and hasattr(user, 'gmail_credentials'):
        gmail_service = GmailService(credentials=user.gmail_credentials)
        emails = gmail_service.get_recent_emails()
    
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "settings": settings,
            "user": user,
            "emails": emails
        }
    )

@app.get("/login")
async def login(request: Request):
    # Generate state token
    state = secrets.token_urlsafe(32)
    state_tokens[state] = True
    
    # Create OAuth flow
    flow = GmailService.create_flow(
        settings.GMAIL_CLIENT_ID,
        settings.GMAIL_CLIENT_SECRET,
        settings.OAUTH_REDIRECT_URI
    )
    
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent',
        state=state,
        scopes=GmailService.SCOPES
    )
    
    return RedirectResponse(authorization_url)

@app.get("/oauth2_callback")
async def oauth2_callback(request: Request, db: Session = Depends(get_db)):
    # Check for error parameter which Google returns when authentication fails
    error = request.query_params.get("error")
    if error:
        # Instead of raising an exception, redirect to home with error message
        return RedirectResponse(
            url=f"/?error=true&email={request.query_params.get('email', '')}", 
            status_code=303
        )

    state = request.query_params.get("state")
    if state not in state_tokens:
        raise HTTPException(status_code=400, detail="Invalid state token")
    
    flow = GmailService.create_flow(
        settings.GMAIL_CLIENT_ID,
        settings.GMAIL_CLIENT_SECRET,
        settings.OAUTH_REDIRECT_URI
    )
    
    try:
        # Get credentials
        flow.fetch_token(
            authorization_response=str(request.url)
        )
        credentials = flow.credentials
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch token: {str(e)}")
    
    # Get user email
    gmail_service = GmailService(credentials=credentials)
    user_info = gmail_service.service.users().getProfile(userId='me').execute()
    email = user_info['emailAddress']
    
    # Create or update user
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email)
        db.add(user)
    
    # Create Gmail service and store serialized credentials
    gmail_service = GmailService(credentials=credentials)
    credentials_json = gmail_service.credentials_to_json()
    if credentials_json:
        user.gmail_credentials = credentials_json
    db.commit()
    
    # Set session
    request.session["user_id"] = user.id
    
    return RedirectResponse(url="/")

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/")

@app.get("/refresh")
async def refresh(request: Request, db: Session = Depends(get_db)):
    if "user_id" not in request.session:
        return RedirectResponse(url="/login", status_code=303)
    
    # Redirect back to home page which will load fresh emails
    return RedirectResponse(url="/", status_code=303)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
