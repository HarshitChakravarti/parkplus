import json
import logging
from datetime import datetime
from redis import Redis
from sqlalchemy.orm import Session
from app.models.vehicle_state import CurrentVehicleState

logger = logging.getLogger(__name__)

REDIS_KEY_PREFIX = "vehicle:state:"
STATE_TTL_SECONDS = 60 * 60 * 24  # 24 hours


def _make_key(plate: str) -> str:
    return f"{REDIS_KEY_PREFIX}{plate}"


def set_vehicle_state(r: Redis, plate: str, floor: int | None, status: str, last_seen: datetime):
    """Write current vehicle state to Redis."""
    payload = {
        "plate": plate,
        "current_floor": floor,
        "status": status,
        "last_seen": last_seen.isoformat(),
    }
    r.setex(_make_key(plate), STATE_TTL_SECONDS, json.dumps(payload))


def get_vehicle_state(r: Redis, plate: str, db: Session) -> dict | None:
    """Read state from Redis; fall back to Postgres on cache miss."""
    try:
        raw = r.get(_make_key(plate))
        if raw:
            return json.loads(raw)
    except Exception as redis_err:
        logger.warning(f"Redis read failed for {plate}, falling back to Postgres: {redis_err}")

    # Cache miss or Redis down — reconstruct from Postgres
    state = db.query(CurrentVehicleState).filter(
        CurrentVehicleState.plate_number == plate
    ).first()

    if not state:
        return None

    # Re-warm the cache
    try:
        set_vehicle_state(r, plate, state.current_floor, state.status, state.last_seen)
    except Exception:
        pass  # Can't re-warm cache, that's fine

    return {
        "plate": state.plate_number,
        "current_floor": state.current_floor,
        "status": state.status,
        "last_seen": state.last_seen.isoformat(),
    }


def delete_vehicle_state(r: Redis, plate: str):
    """Remove state from Redis (e.g. on exit cleanup)."""
    r.delete(_make_key(plate))
