from fastapi import Depends, HTTPException
from starlette import status
from utils.jwt import get_current_user

def require_admin(current_user: dict = Depends(get_current_user)):
    """
    FastAPI dependency — raises 403 if the JWT user is not an admin.
    Usage:  @router.post("/...", dependencies=[Depends(require_admin)])
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user