from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserCreate, UserOut
from app.schemas.auth import Token
from app.services import auth_service
from pydantic import BaseModel
from app.schemas.auth import Token, LoginRequest
from app.utils.dependencies import get_current_user
from app.schemas.user import UserOut
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=UserOut)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    return auth_service.create_user(user, db)

@router.post("/login", response_model=Token)
def login(form_data: LoginRequest, db: Session = Depends(get_db)):
    print("Login endpoint called with:", form_data.username)
    user = auth_service.authenticate_user(form_data.username, form_data.password, db)
    print("User found:", user)
    if not user:
        print("Invalid credentials")
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = auth_service.generate_token(user.id)
    print("Token generated:", token)
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user