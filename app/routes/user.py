from fastapi import APIRouter, Depends, HTTPException, Response, Cookie, status

# Auth
from auth.oauth2 import create_access_token, verify_refresh_token, create_refresh_token, get_current_user

# Database
from database import get_db
from sqlalchemy.orm import Session
from models import User as UserModel
from schemas import UserCreate, create_response
from crud.user_crud import create_user

from util.examples import common_examples, create_example_response
import bcrypt

from config import Config

router = APIRouter()
@router.post(
    "/signup",
    responses={
        200: create_example_response("Signup successful", common_examples["signup_success"]),
        400: create_example_response("User already registered", common_examples["error_400"]),
    },
)
def create_new_user(user: UserCreate, db: Session = Depends(get_db)):
    # 이메일 중복 확인
    db_user = db.query(UserModel).filter(UserModel.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="User already registered")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(user.password.encode("utf-8"), salt)
    user.password = hashed_password
    new_user = create_user(db, user)
    return create_response(200, True, "User created successfully", {"id": new_user.id, "username": new_user.username})
# 로그인 API
@router.post(
    "/login",
    responses={
        200: create_example_response("Login successful", common_examples["login_success"]),
        400: create_example_response("Invalid credentials", common_examples["error_400"]),
    },
)
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

    data = {"access_token": access_token, "token_type": "bearer"}
    return create_response(200, True, "Login successful", data)
# Access Token 갱신 API
@router.post(
    "/refresh",
    responses={
        200: create_example_response("Token refreshed successfully", common_examples["refresh_success"]),
        401: create_example_response("Refresh token missing or invalid", common_examples["error_401_missing_refresh"]),
    },
)
def refresh_token(refresh_token: str = Cookie(None)):
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is missing",
        )

    username = verify_refresh_token(refresh_token)

    new_access_token = create_access_token(data={"sub": username})

    data = {"access_token": new_access_token, "token_type": "bearer"}
    return create_response(200, True, "Token refreshed successfully", data)
@router.get(
    "/users/me",
    responses={
        200: create_example_response("User retrieved successfully", common_examples["user_retrieved"]),
        401: create_example_response("Unauthorized access", common_examples["error_401_invalid_token"]),
    },
)
async def read_users_me(current_user: str = Depends(get_current_user)):
    return create_response(200, True, "User retrieved successfully", {"username": current_user})