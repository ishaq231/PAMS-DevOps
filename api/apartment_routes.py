from . import db_path  # noqa: F401

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel as PydanticModel

from .auth import require_roles

from apartment_models import Apartment

router = APIRouter()


@router.get("/apartments/count")
def apartment_count(user: dict = Depends(require_roles("Administrator", "Manager"))):
    return {"count": Apartment.get_apartment_count()}


@router.get("/apartments")
def list_apartments(user: dict = Depends(require_roles("Administrator", "Manager", "Front Desk Staff"))):
    return [a.to_dict() for a in Apartment.get_all_apartments()]


class ApartmentUpdateRequest(PydanticModel):
    apartment_number: str
    location_city: str
    type: str
    monthly_rent: float
    number_of_rooms: int
    square_footage: float
    occupation_status: str


@router.put("/apartments/{apartment_id}")
def update_apartment(apartment_id: int, payload: ApartmentUpdateRequest, user: dict = Depends(require_roles("Administrator"))):
    updated = Apartment(apartment_id=apartment_id).update_apartment(
        payload.apartment_number, payload.location_city, payload.type,
        payload.monthly_rent, payload.number_of_rooms,
        payload.square_footage, payload.occupation_status,
    )
    if not updated:
        raise HTTPException(status_code=400, detail="Could not update, check the location city is valid")
    return {"apartment_id": apartment_id, "updated": True}


class StatusUpdateRequest(PydanticModel):
    status: str


@router.patch("/apartments/{apartment_id}/status")
def update_apartment_status(apartment_id: int, payload: StatusUpdateRequest, user: dict = Depends(require_roles("Administrator", "Manager"))):
    updated = Apartment(apartment_id=apartment_id).update_apartment_status(payload.status)
    if not updated:
        raise HTTPException(status_code=400, detail="Could not update status")
    return {"apartment_id": apartment_id, "status": payload.status}


class RentUpdateRequest(PydanticModel):
    monthly_rent: float


@router.patch("/apartments/{apartment_id}/rent")
def update_apartment_rent(apartment_id: int, payload: RentUpdateRequest, user: dict = Depends(require_roles("Administrator"))):
    updated = Apartment(apartment_id=apartment_id).update_apartment_rent(payload.monthly_rent)
    if not updated:
        raise HTTPException(status_code=400, detail="Could not update rent")
    return {"apartment_id": apartment_id, "monthly_rent": payload.monthly_rent}