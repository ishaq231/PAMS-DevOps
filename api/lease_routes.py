from . import db_path  # noqa: F401

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel as PydanticModel

from .auth import require_roles, require_staff_or_self

from lease_models import LeaseAgreement

router = APIRouter()


@router.get("/leases")
def list_leases(user: dict = Depends(require_roles("Administrator", "Manager"))):
    return [l.to_dict() for l in LeaseAgreement.get_all_leases()]


@router.get("/tenants/{tenant_id}/leases")
def list_leases_for_tenant(tenant_id: int, user: dict = Depends(require_staff_or_self("Administrator", "Manager"))):
    return [l.to_dict() for l in LeaseAgreement.get_leases_for_user(tenant_id)]


class LeaseCreateRequest(PydanticModel):
    tenant_id: int
    apartment_id: int
    start_date: str
    end_date: str
    monthly_rent: float
    deposit: float
    term_months: int


@router.post("/leases", status_code=201)
def create_lease(payload: LeaseCreateRequest, user: dict = Depends(require_roles("Administrator", "Manager"))):
    created = LeaseAgreement.create_lease(
        payload.tenant_id, payload.apartment_id, payload.start_date,
        payload.end_date, payload.monthly_rent, payload.deposit, payload.term_months,
    )
    if not created:
        raise HTTPException(status_code=400, detail="Could not create lease")
    return {"created": True}


class LeaseUpdateRequest(PydanticModel):
    start_date: str
    end_date: str
    monthly_rent: float
    term_months: int
    status: str


@router.put("/leases/{lease_id}")
def update_lease(lease_id: int, payload: LeaseUpdateRequest, user: dict = Depends(require_roles("Administrator", "Manager"))):
    updated = LeaseAgreement(leaseID=lease_id).update_lease(
        payload.start_date, payload.end_date, payload.monthly_rent,
        payload.term_months, payload.status,
    )
    if not updated:
        raise HTTPException(status_code=400, detail="Could not update lease")
    return {"lease_id": lease_id, "updated": True}


class LeaseStatusUpdate(PydanticModel):
    status: str


@router.patch("/leases/{lease_id}/status")
def update_lease_status(lease_id: int, payload: LeaseStatusUpdate, user: dict = Depends(require_roles("Administrator", "Manager"))):
    updated = LeaseAgreement(leaseID=lease_id).update_lease_status(payload.status)
    if not updated:
        raise HTTPException(status_code=400, detail="Could not update lease status")
    return {"lease_id": lease_id, "status": payload.status}


@router.post("/leases/{lease_id}/terminate")
def terminate_lease(lease_id: int, user: dict = Depends(require_roles("Administrator", "Manager"))):
    terminated = LeaseAgreement(leaseID=lease_id).terminate_lease()
    if not terminated:
        raise HTTPException(status_code=400, detail="Could not terminate lease")
    return {"lease_id": lease_id, "status": "TERMINATED"}