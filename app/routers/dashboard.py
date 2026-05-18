from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.vehicle import OccupancyResponse, EventHistoryResponse
from app.services.dashboard_service import get_occupancy, get_event_history
from app.ws_manager import manager

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # keep connection alive
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.get("/occupancy", response_model=OccupancyResponse)
def occupancy(db: Session = Depends(get_db)):
    return get_occupancy(db)


@router.get("/events", response_model=list[EventHistoryResponse])
def event_history(
    plate: str | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, le=200),
    db: Session = Depends(get_db),
):
    return get_event_history(db, plate, skip, limit)
