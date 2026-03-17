from datetime import timedelta, datetime, timezone
import os
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from repositories.auth_repository import get_user_by_email
from passlib.context import CryptContext
from jose import JWTError, jwt
from starlette import status
from database import get_db
from typing import Annotated

def authenticate_user(username: str, password: str, db, bcrypt_context: CryptContext):
    user = get_user_by_email(db, username)
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM"))

def get_current_user(
    request: Request,
    db: Annotated[Session, Depends(get_db)]
):
    """
    Reads JWT from cookie, validates it, then fetches the live user row
    so that role is always up-to-date (not stale from token).
    """
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    try:
        payload = jwt.decode(
            token,
            os.getenv("SECRET_KEY"),
            algorithms=[os.getenv("ALGORITHM")]
        )
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate user"
            )
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    user = get_user_by_email(db, username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists"
        )

    return {
        "username": user.email,
        "id": user.id,
        "role": user.role          
    }