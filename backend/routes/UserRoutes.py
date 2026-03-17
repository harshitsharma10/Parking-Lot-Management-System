from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from utils.jwt import get_current_user
from schemas.UserRequest import CreateUserRequest
from database import get_db
from services import auth
from starlette import status
from schemas.UserRequest import UserLogin
from fastapi import Response

router = APIRouter(prefix="/auth",tags=["USERS"]) 

db_dependency = Annotated[Session, Depends(get_db)]

@router.post("/sign-up", status_code=status.HTTP_201_CREATED)
def create_user(db : db_dependency, user_req :CreateUserRequest):
    return auth.create_user(db, user_req)

@router.post("/login", status_code=status.HTTP_200_OK)
def login_user(
    response: Response,
    db: db_dependency,
    user_req: UserLogin
):
    token = auth.login_user(db, user_req)

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,     
        samesite="lax",
        domain=None,
        max_age=1200
    )

    return {"message": "Login successful"}

@router.get("/me")
def get_me(current_user: Annotated[dict, Depends(get_current_user)]):
    return current_user  

@router.post("/logout", status_code=status.HTTP_200_OK)
def logout_user(
    response: Response,
    _: Annotated[dict, Depends(get_current_user)]
):
    response.delete_cookie(
        key="access_token",
        httponly=True,
        samesite="none",
        secure=False,
        path="/",
    )
    return {"message": "Logged out successfully"}