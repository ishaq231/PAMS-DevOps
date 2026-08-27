from . import db_path  # noqa: F401

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel as PydanticModel

from .auth import require_roles

from location_models import Location

router = APIRouter()


@router.get("/locations")
def list_locations(user: dict = Depends(require_roles("Administrator", "Manager", "Front Desk Staff", "Finance Manager", "Maintenance Staff"))):
    return [l.to_dict() for l in Location.get_all_locations()]


class LocationCreateRequest(PydanticModel):
    city: str
    manager: str


@router.post("/locations", status_code=201)
def create_location(payload: LocationCreateRequest, user: dict = Depends(require_roles("Administrator"))):
    location_id = Location.add_location(payload.city, payload.manager)
    if location_id is None:
        raise HTTPException(status_code=400, detail="Could not create location")
    return {"location_id": location_id}