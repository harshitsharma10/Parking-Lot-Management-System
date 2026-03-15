from datetime import timedelta
from fastapi import HTTPException
from passlib.context import CryptContext
from models.user_model import User
from schemas.UserRequest import CreateUserRequest
from sqlalchemy.orm import Session
from schemas.UserRequest import UserLogin
from starlette import status
from repositories import auth_repository
from utils import jwt
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def create_user(db: Session, user_req: CreateUserRequest):
    existing_user = auth_repository.get_user_by_email(db, user_req.email)
 
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists") 
    user = User(
        name = user_req.name,
        email = user_req.email,
        hashed_password = bcrypt_context.hash(user_req.password),
    )
 
    return auth_repository.create_user(db, user)


def login_user(db: Session, user_req: UserLogin):
    user = jwt.authenticate_user(
        user_req.email,
        user_req.password,
        db,
        bcrypt_context
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token = jwt.create_access_token(
        username=user.email,
        user_id=user.id,
        expires_delta=timedelta(minutes=20)
    )

    return access_token

# raise HTTPException(status_code=404, detail="User not found!")

# raise HTTPException(status_code=401, detail='Invalid credentials')