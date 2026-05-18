from fastapi import FastAPI
from app.routers import events, vehicles, dashboard

app = FastAPI(title="ParkPulse", version="0.1.0")

app.include_router(events.router)
app.include_router(vehicles.router)
app.include_router(dashboard.router)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "parkpulse"}
