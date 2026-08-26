from . import db_path  # noqa: F401

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel as PydanticModel

from frontdesk_models import Complaint, Enquiry

from .common import get_or_404

router = APIRouter()


# --- Complaints ---

@router.get("/complaints/stats")
def complaint_stats():
    return Complaint.get_complaint_stats()


@router.get("/complaints")
def list_complaints():
    complaints = Complaint.get_all_complaints()
    return [c.to_dict() for c in complaints]


@router.get("/complaints/{complaint_id}")
def get_complaint(complaint_id: int):
    complaint = get_or_404(
        Complaint.get_complaint_by_id(complaint_id),
        "Complaint not found",
    )
    return complaint.to_dict()


@router.get("/tenants/{tenant_id}/complaints")
def list_complaints_for_tenant(tenant_id: int):
    complaints = Complaint.get_complaints_for_tenant(tenant_id)
    return [c.to_dict() for c in complaints]


class ComplaintCreateRequest(PydanticModel):
    tenant_id: int
    subject: str
    description: str


@router.post("/complaints", status_code=201)
def create_complaint(payload: ComplaintCreateRequest):
    complaint_id = Complaint.create_complaint(
        tenant_id=payload.tenant_id,
        subject=payload.subject,
        description=payload.description,
    )
    if complaint_id is None:
        raise HTTPException(status_code=400, detail="Could not create complaint")
    return {"complaint_id": complaint_id}


class ComplaintStatusUpdate(PydanticModel):
    status: str


@router.patch("/complaints/{complaint_id}")
def update_complaint_status(complaint_id: int, payload: ComplaintStatusUpdate):
    updated = Complaint(complaint_id=complaint_id).update_complaint_status(payload.status)
    if not updated:
        raise HTTPException(status_code=400, detail="Could not update complaint status")
    return {"complaint_id": complaint_id, "status": payload.status}


@router.delete("/complaints/{complaint_id}")
def delete_complaint(complaint_id: int):
    deleted = Complaint(complaint_id=complaint_id).delete_complaint()
    if not deleted:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return {"complaint_id": complaint_id, "deleted": True}


# --- Enquiries ---

@router.get("/enquiries")
def list_enquiries():
    enquiries = Enquiry.get_all_enquiries()
    return [e.to_dict() for e in enquiries]


@router.get("/tenants/{tenant_id}/enquiries")
def list_enquiries_for_tenant(tenant_id: int):
    enquiries = Enquiry.get_enquiries_for_tenant(tenant_id)
    return [e.to_dict() for e in enquiries]


class EnquiryCreateRequest(PydanticModel):
    tenant_name: str
    enquiry_details: str
    handled_by: str
    tenant_id: Optional[int] = None


@router.post("/enquiries", status_code=201)
def create_enquiry(payload: EnquiryCreateRequest):
    enquiry_id = Enquiry.create_enquiry(
        tenant_name=payload.tenant_name,
        enquiry_details=payload.enquiry_details,
        handled_by=payload.handled_by,
        tenant_id=payload.tenant_id,
    )
    if enquiry_id is None:
        raise HTTPException(status_code=400, detail="Could not create enquiry")
    return {"enquiry_id": enquiry_id}