from fastapi import APIRouter
from pydantic import BaseModel
from Server.services.tracker import Tracker

router = APIRouter()
tracker = Tracker()

class LogParamRequest(BaseModel):
    run_id: str
    key: str
    value: str

@router.post("/param/log")
def log_param(request: LogParamRequest):
    param = tracker.log_param(request.run_id, request.key, request.value)
    return{
        "id": param.id,
        "run_id": param.run_id,
        "status": "OK"
        }

class LogMetric(BaseModel):
    run_id: str
    key: str
    value: float
    step: int = 0

@router.post("/metric/log")
def log_metric(request: LogMetric):
    tracker.log_metric(request.run_id, request.key, request.value, request.step)
    return{
        "status": "ok"
    }


class Logartifact(BaseModel):
    run_id: str
    file_path: str


@router.post("/artifacts/log")
def log_artifact(request: Logartifact):
    artifact = tracker.log_artifact(request.run_id, request.file_path)
    return {"path": artifact.path}
