from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.redis_client import get_redis
from app.services.state_service import get_vehicle_state
from app.services.vehicle_service import get_vehicle_detail, register_vehicle
from app.schemas.vehicle import VehicleRegisterRequest, VehicleRegisterResponse

router = APIRouter(prefix="/vehicles", tags=["Vehicles"])

@router.post("/register", response_model=VehicleRegisterResponse, status_code=201)
def register(payload: VehicleRegisterRequest, db: Session = Depends(get_db)):
    vehicle = register_vehicle(
        db,
        plate=payload.plate_number,
        owner_phone=payload.owner_phone,
        vehicle_type=payload.vehicle_type,
    )
    return VehicleRegisterResponse(
        message="Vehicle registered successfully",
        plate_number=vehicle.plate_number,
        is_registered=vehicle.is_registered,
    )


@router.get("/{plate}/state")
def get_state(plate: str, db: Session = Depends(get_db)):
    r = get_redis()
    state = get_vehicle_state(r, plate.upper(), db)
    if not state:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return state


@router.get("/{plate}")
def get_vehicle(plate: str, db: Session = Depends(get_db)):
    detail = get_vehicle_detail(db, plate.upper())
    if not detail:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return detail
