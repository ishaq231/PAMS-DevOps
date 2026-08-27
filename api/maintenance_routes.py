from . import db_path  # noqa: F401

from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel as PydanticModel

from maintenance_models import Maintenance, MaintenanceLog

from .common import get_or_404
from .auth import require_roles, require_staff_or_self, require_staff_self

router = APIRouter()


@router.get("/maintenance/stats")
def maintenance_stats(user: dict = Depends(require_roles("Administrator", "Manager", "Front Desk Staff", "Maintenance Staff"))):
    return Maintenance.get_maintenance_stats()


@router.get("/maintenance/staff")
def maintenance_staff(user: dict = Depends(require_roles("Administrator", "Manager", "Front Desk Staff"))):
    return Maintenance.get_all_staff()


@router.get("/maintenance/staff/availability")
def maintenance_staff_availability(user: dict = Depends(require_roles("Administrator", "Manager", "Front Desk Staff", "Maintenance Staff"))):
    return Maintenance.get_staff_availability()


@router.get("/maintenance/logs")
def all_maintenance_logs(user: dict = Depends(require_roles("Administrator", "Manager", "Maintenance Staff"))):
    return [l.to_dict() for l in MaintenanceLog.get_all_maintenance_logs()]


@router.get("/maintenance")
def list_maintenance(user: dict = Depends(require_roles("Administrator", "Manager", "Front Desk Staff", "Maintenance Staff"))):
    return [m.to_dict() for m in Maintenance.get_all_maintenance_requests()]


@router.get("/maintenance/{request_id}")
def get_maintenance(request_id: int, user: dict = Depends(require_roles("Administrator", "Manager", "Front Desk Staff", "Maintenance Staff"))):
    request = get_or_404(
        Maintenance.get_request_by_id(request_id),
        "Maintenance request not found",
    )
    return request.to_dict()


@router.get("/tenants/{tenant_id}/maintenance")
def list_maintenance_for_tenant(tenant_id: int, user: dict = Depends(require_staff_or_self("Administrator", "Manager", "Front Desk Staff", "Maintenance Staff"))):
    return [m.to_dict() for m in Maintenance.get_maintenance_for_tenant(tenant_id)]


@router.get("/staff/{staff_id}/maintenance")
def list_maintenance_for_staff(staff_id: int, user: dict = Depends(require_staff_self("Administrator", "Manager", "Front Desk Staff"))):
    return [m.to_dict() for m in Maintenance.get_maintenance_for_staff(staff_id)]


class MaintenanceCreateRequest(PydanticModel):
    apartment_id: int
    tenant_id: int
    description: str
    priority: str = "Low"
    category: str = "General"


@router.post("/maintenance", status_code=201)
def create_maintenance(payload: MaintenanceCreateRequest, user: dict = Depends(require_roles("Tenant", "Front Desk Staff", "Administrator", "Manager"))):
    if user["role"] == "Tenant" and payload.tenant_id != user["user_id"]:
        raise HTTPException(status_code=403, detail="You can only submit a request under your own account")
    request_id = Maintenance.create_maintenance_request(
        payload.apartment_id, payload.tenant_id, payload.description,
        payload.priority, payload.category,
    )
    if request_id is None:
        raise HTTPException(status_code=400, detail="Could not create maintenance request")
    return {"request_id": request_id}


class StatusUpdateRequest(PydanticModel):
    status: str


@router.patch("/maintenance/{request_id}/status")
def update_maintenance_status(request_id: int, payload: StatusUpdateRequest, user: dict = Depends(require_roles("Administrator", "Manager", "Front Desk Staff", "Maintenance Staff"))):
    updated = Maintenance(request_id=request_id).update_maintenance_status(payload.status)
    if not updated:
        raise HTTPException(status_code=400, detail="Could not update status")
    return {"request_id": request_id, "status": payload.status}


class PriorityUpdateRequest(PydanticModel):
    priority: str


@router.patch("/maintenance/{request_id}/priority")
def update_maintenance_priority(request_id: int, payload: PriorityUpdateRequest, user: dict = Depends(require_roles("Administrator", "Manager", "Front Desk Staff"))):
    updated = Maintenance(request_id=request_id).update_maintenance_priority(payload.priority)
    if not updated:
        raise HTTPException(status_code=400, detail="Could not update priority")
    return {"request_id": request_id, "priority": payload.priority}


class AssignStaffRequest(PydanticModel):
    staff_id: int


@router.post("/maintenance/{request_id}/assign")
def assign_staff(request_id: int, payload: AssignStaffRequest, user: dict = Depends(require_roles("Administrator", "Manager", "Front Desk Staff"))):
    assigned = Maintenance(request_id=request_id).assign_staff_to_request(payload.staff_id)
    if not assigned:
        raise HTTPException(status_code=400, detail="Could not assign staff")
    return {"request_id": request_id, "assigned_staff_id": payload.staff_id}


class ScheduleUpdateRequest(PydanticModel):
    scheduled_date: str


@router.patch("/maintenance/{request_id}/schedule")
def update_schedule(request_id: int, payload: ScheduleUpdateRequest, user: dict = Depends(require_roles("Administrator", "Manager", "Front Desk Staff", "Maintenance Staff"))):
    updated = Maintenance(request_id=request_id).update_scheduled_date(payload.scheduled_date)
    if not updated:
        raise HTTPException(status_code=400, detail="Could not update scheduled date")
    return {"request_id": request_id, "scheduled_date": payload.scheduled_date}


class CostUpdateRequest(PydanticModel):
    cost: float


@router.patch("/maintenance/{request_id}/cost")
def update_cost(request_id: int, payload: CostUpdateRequest, user: dict = Depends(require_roles("Administrator", "Manager", "Maintenance Staff"))):
    updated = Maintenance(request_id=request_id).update_maintenance_cost(payload.cost)
    if not updated:
        raise HTTPException(status_code=400, detail="Could not update cost")
    return {"request_id": request_id, "cost": payload.cost}


@router.get("/maintenance/{request_id}/logs")
def logs_for_request(request_id: int, user: dict = Depends(require_roles("Administrator", "Manager", "Front Desk Staff", "Maintenance Staff"))):
    return [l.to_dict() for l in MaintenanceLog.get_logs_for_request(request_id)]


class LogCreateRequest(PydanticModel):
    description: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    parts_used: Optional[str] = None
    cost_breakdown: Optional[str] = None
    technician_notes: Optional[str] = None


@router.post("/maintenance/{request_id}/logs", status_code=201)
def create_log(request_id: int, payload: LogCreateRequest, user: dict = Depends(require_roles("Administrator", "Manager", "Maintenance Staff"))):
    log_id = MaintenanceLog.create_maintenance_log(
        request_id, payload.start_time, payload.end_time, payload.description,
        payload.parts_used, payload.cost_breakdown, payload.technician_notes,
    )
    if log_id is None:
        raise HTTPException(status_code=400, detail="Could not create log entry")
    return {"log_id": log_id}