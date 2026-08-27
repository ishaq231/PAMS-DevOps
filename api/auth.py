import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY is not set")

ALGORITHM = "HS256"
TOKEN_EXPIRY_HOURS = 8

bearer_scheme = HTTPBearer()


def create_access_token(user: dict) -> str:
    """Build a signed token describing who this user is."""
    payload = {
        "sub": str(user["user_id"]),
        "name": user["name"],
        "role": user["role"],
        "location_id": user.get("location_id"),
        "location_name": user.get("location_name"),
        "exp": datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRY_HOURS),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> dict:
    """Read and verify the token from the Authorization header."""
    try:
        payload = jwt.decode(creds.credentials, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired, please log in again")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    return {
        "user_id": int(payload["sub"]),
        "name": payload["name"],
        "role": payload["role"],
        "location_id": payload.get("location_id"),
        "location_name": payload.get("location_name"),
    }


def require_roles(*allowed_roles):
    """Build a dependency that only lets certain roles through."""
    def checker(user: dict = Depends(get_current_user)) -> dict:
        if user["role"] not in allowed_roles:
            raise HTTPException(status_code=403, detail="You don't have permission to do that")
        return user
    return checker
def require_staff_or_self(*staff_roles, path_param: str = "tenant_id"):
    """Lets the listed staff roles through, or a user viewing/acting on their own record.

    `path_param` must match the name of the route's path parameter being checked
    against the caller's user_id (FastAPI binds it by name).
    """
    def checker(request: Request, user: dict = Depends(get_current_user)) -> dict:
        record_id = request.path_params.get(path_param)
        if user["role"] in staff_roles or (record_id is not None and user["user_id"] == int(record_id)):
            return user
        raise HTTPException(status_code=403, detail="You can only access your own data")
    return checker
def require_staff_self(*staff_roles):
    """Same idea as require_staff_or_self, but checks a `staff_id` path param —
    for a Maintenance Staff member viewing their own assigned request queue."""
    def checker(staff_id: int, user: dict = Depends(get_current_user)) -> dict:
        if user["role"] in staff_roles or user["user_id"] == staff_id:
            return user
        raise HTTPException(status_code=403, detail="You can only access your own data")
    return checker

def require_user_self_or_staff(*staff_roles):
    """Same self-or-staff pattern, but checks a `user_id` path param —
    for a user (tenant or staff) viewing or managing their own account."""
    def checker(user_id: int, user: dict = Depends(get_current_user)) -> dict:
        if user["role"] in staff_roles or user["user_id"] == user_id:
            return user
        raise HTTPException(status_code=403, detail="You can only access your own data")
    return checker