from fastapi import APIRouter, Depends, HTTPException, Response, Cookie, status

# Auth
from auth.oauth2 import create_access_token, verify_refresh_token, create_refresh_token, get_current_user

# Database
from database import get_db
from sqlalchemy.orm import Session
from models import User as UserModel
from schemas import UserCreate, User
from crud import create_user
import bcrypt

from typing import Dict
from config import Config

router = APIRouter()
@router.post("/signup", response_model=User)
def create_new_user(user: UserCreate, db: Session = Depends(get_db)):
    # 이메일 중복 확인
    db_user = db.query(UserModel).filter(UserModel.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(user.password.encode("utf-8"), salt)
    user.password = hashed_password

    return create_user(db, user)

# 로그인 API
@router.post("/login", response_model=Dict[str, str])
def login(request: UserCreate, response: Response, db: Session = Depends(get_db)):
    # 사용자 확인
    db_user = db.query(UserModel).filter(UserModel.username == request.username).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Incorrect username")
    if not bcrypt.checkpw(request.password.encode('utf-8'), db_user.password.encode('utf-8')):
        raise HTTPException(status_code=400, detail="Incorrect password")

    # Access Token 및 Refresh Token 생성
    access_token = create_access_token(data={"sub": db_user.username})
    refresh_token = create_refresh_token(data={"sub": db_user.username})

    # HTTP-only 쿠키에 Refresh Token 저장
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=Config.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    return {"access_token": access_token, "token_type": "bearer"}
# Access Token 갱신 API
@router.post("/refresh", response_model=Dict[str, str])
def refresh_token(refresh_token: str = Cookie(None)):
    """
    Refresh Token을 쿠키에서 가져와 검증하고 Access Token을 갱신합니다.
    """
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is missing",
        )

    # Refresh Token 검증
    username = verify_refresh_token(refresh_token)

    # 새로운 Access Token 발급
    new_access_token = create_access_token(data={"sub": username})

    return {"access_token": new_access_token, "token_type": "bearer"}

@router.get("/users/me")
async def read_users_me(current_user: str = Depends(get_current_user)):
    return {"username": current_user}