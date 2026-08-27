from . import db_path  # noqa: F401

from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi import Depends
from pydantic import BaseModel as PydanticModel
from .common import get_or_404
from .auth import require_roles, require_staff_or_self

from tenant_models import Tenant
from user_models import User as UserAccount

router = APIRouter()


@router.get("/tenants")
def list_tenants(user: dict = Depends(require_roles("Administrator", "Manager", "Front Desk Staff", "Finance Manager"))):
    tenants = Tenant.get_all_tenants()
    result = []
    for t in tenants:
        data = t.to_dict()
        data["tenant_id"] = data.get("user_id")
        result.append(data)
    return result


@router.get("/tenants/{tenant_id}")
def get_tenant(tenant_id: int, user: dict = Depends(require_staff_or_self("Administrator", "Manager", "Front Desk Staff", "Finance Manager"))):
    tenant = get_or_404(
        Tenant(tenant_id=tenant_id).get_tenant_profile(),
        "Tenant not found",
    )
    return tenant.to_dict()


class TenantCreateRequest(PydanticModel):
    fname: str
    lname: str
    email: str
    phone: str
    dob: str
    username: str
    password: str
    occupation: Optional[str] = None
    ni_number: Optional[str] = None
    references: Optional[str] = None


@router.post("/tenants", status_code=201)
def create_tenant(payload: TenantCreateRequest, user: dict = Depends(require_roles("Administrator", "Front Desk Staff"))):
    new_id = UserAccount.admin_add_user(
        fname=payload.fname,
        lname=payload.lname,
        email=payload.email,
        phone=payload.phone,
        dob=payload.dob,
        role="Tenant",
        username=payload.username,
        password=payload.password,
        occupation=payload.occupation,
        ni_number=payload.ni_number,
        references=payload.references,
    )
    if new_id is None:
        raise HTTPException(status_code=400, detail="Could not create tenant")
    return {"tenant_id": new_id}