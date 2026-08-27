from . import db_path  # noqa: F401

from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel as PydanticModel

from user_models import User, StaffMember

from .common import get_or_404
from .auth import require_roles, require_user_self_or_staff

router = APIRouter()


@router.get("/users/count")
def user_count(user: dict = Depends(require_roles("Administrator", "Manager"))):
    return {"count": User.get_user_count()}


@router.get("/users")
def list_users(user: dict = Depends(require_roles("Administrator", "Manager"))):
    return [u.to_dict() for u in User.get_all_users()]


@router.get("/users/{user_id}")
def get_user(user_id: int, user: dict = Depends(require_user_self_or_staff("Administrator", "Manager"))):
    target = get_or_404(User.get_user_by_id(user_id), "User not found")
    return target.to_dict()


class UserCreateRequest(PydanticModel):
    fname: str
    lname: str
    email: str
    phone: str
    dob: str
    role: str
    username: str
    password: str
    occupation: Optional[str] = None
    ni_number: Optional[str] = None
    references: Optional[str] = None


@router.post("/users", status_code=201)
def create_user(payload: UserCreateRequest, user: dict = Depends(require_roles("Administrator", "Manager"))):
    new_id = User.admin_add_user(
        fname=payload.fname, lname=payload.lname, email=payload.email,
        phone=payload.phone, dob=payload.dob, role=payload.role,
        username=payload.username, password=payload.password,
        occupation=payload.occupation, ni_number=payload.ni_number,
        references=payload.references,
    )
    if new_id is None:
        raise HTTPException(status_code=400, detail="Could not create user")
    return {"user_id": new_id}


class UserUpdateRequest(PydanticModel):
    fname: str
    lname: str
    email: str
    phone: str
    dob: str
    role: str
    username: str
    occupation: Optional[str] = None
    ni_number: Optional[str] = None
    references: Optional[str] = None


@router.put("/users/{user_id}")
def update_user(user_id: int, payload: UserUpdateRequest, user: dict = Depends(require_roles("Administrator", "Manager"))):
    updated = User(user_id=user_id).update_user(
        payload.fname, payload.lname, payload.email, payload.phone,
        payload.dob, payload.role, payload.username,
        occupation=payload.occupation, ni_number=payload.ni_number,
        references=payload.references,
    )
    if not updated:
        raise HTTPException(status_code=400, detail="Could not update user")
    return {"user_id": user_id, "updated": True}


@router.delete("/users/{user_id}")
def delete_user(user_id: int, user: dict = Depends(require_roles("Administrator"))):
    deleted = User(user_id=user_id).delete_user()
    if not deleted:
        raise HTTPException(status_code=400, detail="Could not delete user")
    return {"user_id": user_id, "deleted": True}


class PasswordChangeRequest(PydanticModel):
    old_password: str
    new_password: str


@router.post("/users/{user_id}/change-password")
def change_password(user_id: int, payload: PasswordChangeRequest, user: dict = Depends(require_user_self_or_staff("Administrator", "Manager"))):
    changed = User(user_id=user_id).change_password(payload.old_password, payload.new_password)
    if not changed:
        raise HTTPException(status_code=400, detail="Old password incorrect or user not found")
    return {"user_id": user_id, "password_changed": True}


@router.get("/staff")
def list_staff(user: dict = Depends(require_roles("Administrator", "Manager"))):
    return [s.to_dict() for s in StaffMember.get_all_staff()]


class StaffUpdateRequest(PydanticModel):
    salary: Optional[float] = None
    role: Optional[str] = None
    start_date: Optional[str] = None
    location_id: Optional[int] = None


@router.patch("/staff/{employee_id}")
def update_staff_member(employee_id: int, payload: StaffUpdateRequest, user: dict = Depends(require_roles("Administrator", "Manager"))):
    updated = StaffMember(employee_id=employee_id).update_staff_member(
        salary=payload.salary, role=payload.role,
        start_date=payload.start_date, location_id=payload.location_id,
    )
    if not updated:
        raise HTTPException(status_code=400, detail="Could not update staff member")
    return {"employee_id": employee_id, "updated": True}