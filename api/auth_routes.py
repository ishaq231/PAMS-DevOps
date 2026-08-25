from . import db_path  # noqa: F401 — importing this runs the sys.path fix above

from fastapi import APIRouter, HTTPException
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
    return result