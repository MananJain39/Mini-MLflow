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

class EndRunRequest(BaseModel):
    run_id: str

@router.post("/run/end")
def end_run(request: EndRunRequest):
    run = tracker.end_run(request.run_id)
    return {
        "id": run.id,
        "end_time": run.end_time,
        "status": run.status,
    }
