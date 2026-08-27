from . import db_path  # noqa: F401 — importing this runs the sys.path fix above

from fastapi import APIRouter, HTTPException
from fastapi import Depends 
from .auth import create_access_token, get_current_user
from pydantic import BaseModel as PydanticModel

from auth_models import User

router = APIRouter()


class LoginRequest(PydanticModel):
    username: str
    password: str


@router.post("/login")
def login(payload: LoginRequest):
    result = User.login(payload.username, payload.password)
    if not result:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {
        "access_token": create_access_token(result),
        "token_type": "bearer",
        "user": result,
    }
@router.get("/me")
def me(user: dict = Depends(get_current_user)):
    return user