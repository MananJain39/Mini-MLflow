from fastapi import APIRouter
from mini_mlflow.Server.services.tracker import Tracker
from mini_mlflow.Server.API.models import (
    LogParamRequest, LogMetricRequest, LogArtifactRequest, ArtifactResponse,
    LogTagRequest, TagResponse
)

router = APIRouter()
tracker = Tracker()

@router.post("/param/log")
def log_param(request: LogParamRequest):
    param = tracker.log_param(request.run_id, request.key, request.value)
    return{
        "id": param.id,
        "run_id": param.run_id,
        "status": "OK"
        }

@router.post("/metric/log")
def log_metric(request: LogMetricRequest):
    tracker.log_metric(request.run_id, request.key, request.value, request.step)
    return{
        "status": "ok"
    }



@router.post("/artifacts/log", response_model=ArtifactResponse)
def log_artifact(request: LogArtifactRequest):
    artifact = tracker.log_artifact(request.run_id, request.file_path)
    return ArtifactResponse(path=artifact.path)

@router.post("/tag/log", response_model=TagResponse)
def log_tag(request: LogTagRequest):
    tag = tracker.log_tag(request.run_id, request.key, request.value)
    return TagResponse(key=tag.key, value=tag.value)
