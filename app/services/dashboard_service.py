from sqlalchemy.orm import Session
from app.models.vehicle_state import CurrentVehicleState
from app.models.vehicle_event import VehicleEvent


def get_occupancy(db: Session) -> dict:
    """Count vehicles currently inside, grouped by floor."""
    inside = (
        db.query(CurrentVehicleState)
        .filter(CurrentVehicleState.status == "inside")
        .all()
    )

    total = len(inside)

    floor_counts: dict[int, int] = {}
    for v in inside:
        if v.current_floor is not None:
            floor_counts[v.current_floor] = floor_counts.get(v.current_floor, 0) + 1

    by_floor = [{"floor": f, "count": c} for f, c in sorted(floor_counts.items())]

    return {"total_inside": total, "by_floor": by_floor}


def get_event_history(db: Session, plate: str | None, skip: int, limit: int) -> list:
    """Paginated event log, optionally filtered by plate."""
    query = db.query(VehicleEvent).order_by(VehicleEvent.timestamp.desc())

    if plate:
        query = query.filter(VehicleEvent.plate_number == plate.upper())

    return query.offset(skip).limit(limit).all()
