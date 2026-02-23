from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from starlette.templating import Jinja2Templates
import os
from sqlalchemy.orm import Session
from .utils import hash_password, verify_password
from .database import SessionLocal
from .models import User

router = APIRouter()
templates = Jinja2Templates(directory=os.path.join(os.getcwd(), "templates"))

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/signup")
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@router.post("/signup")
async def signup(request: Request, name: str = Form(...), email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        return RedirectResponse("/login?error=exists", status_code=303)
    u = User(name=name, email=email, password_hash=hash_password(password))
    db.add(u)
    db.commit()
    request.session["user"] = {"id": u.id, "email": u.email, "name": u.name, "role": u.role}
    return RedirectResponse("/dashboard", status_code=303)

@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    u = db.query(User).filter(User.email == email).first()
    if not u or not verify_password(password, u.password_hash):
        return RedirectResponse("/login?error=invalid", status_code=303)
    request.session["user"] = {"id": u.id, "email": u.email, "name": u.name, "role": u.role}
    return RedirectResponse("/dashboard", status_code=303)

@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)
