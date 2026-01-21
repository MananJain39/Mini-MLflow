from fastapi import APIRouter
from pydantic import BaseModel
from Server.services.tracker import Tracker

router = APIRouter()
tracker = Tracker()

class StartRunRequest(BaseModel):
    experiment_id: str

@router.post("/run/start")
def start_run(request: StartRunRequest):
    run = tracker.start_run(request.experiment_id)
    return {
        "id": run.id,
        "experiment_id": run.experiment_id,
        "start_time": run.start_time,
        "status": run.status
    }