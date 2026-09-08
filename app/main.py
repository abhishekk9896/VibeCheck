import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from typing import List
from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import engine, Base, get_db
from app import models, schemas, auth
from app.worker import run_audit_task

Base.metadata.create_all(bind=engine)

app = FastAPI(title="VibeCheck API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Authentication Routes ---
@app.post("/auth/signup", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pwd = auth.get_password_hash(user_in.password)
    user = models.User(email=user_in.email, hashed_password=hashed_pwd)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.post("/auth/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/auth/me", response_model=schemas.UserResponse)
def get_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

# --- Audit Routes ---
@app.post("/audits", response_model=schemas.AuditSessionResponse, status_code=status.HTTP_201_CREATED)
def create_audit(
    audit_in: schemas.AuditSessionCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    session = models.AuditSession(
        user_id=current_user.id,
        repo_source=audit_in.repo_source,
        status="IN_PROGRESS"
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    # Trigger background worker execution
    background_tasks.add_task(
        run_audit_task,
        session_id=session.id,
        repo_source=audit_in.repo_source,
        scope_content=audit_in.scope_content
    )
    return session

@app.get("/audits", response_model=List[schemas.AuditSessionResponse])
def list_audits(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return db.query(models.AuditSession).filter(models.AuditSession.user_id == current_user.id).all()

@app.get("/audits/{session_id}", response_model=schemas.AuditSessionResponse)
def get_audit(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    session = db.query(models.AuditSession).filter(
        models.AuditSession.id == session_id,
        models.AuditSession.user_id == current_user.id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Audit session not found")
    return session