from fastapi import APIRouter, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.event import ANPREventCreate, ANPREventResponse
from app.services.event_service import process_anpr_event
from app.ws_manager import manager

router = APIRouter(prefix="/events", tags=["Events"])


@router.post("", response_model=ANPREventResponse, status_code=201)
async def ingest_event(payload: ANPREventCreate, db: Session = Depends(get_db)):
    try:
        result = await run_in_threadpool(process_anpr_event, db, payload)

        await manager.broadcast({
            "type": "vehicle_update",
            "plate": result["plate"],
            "floor": result["floor"],
            "status": result["status"],
            "checkpoint": result["checkpoint"],
            "timestamp": result["timestamp"],
        })

        return ANPREventResponse(
            message="Event processed successfully",
            plate=result["plate"],
            checkpoint=result["checkpoint"],
            checkpoint_type=result.get("checkpoint_type"),
            status=result["status"],
            floor=result["floor"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
