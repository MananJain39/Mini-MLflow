from fastapi import APIRouter
from mini_mlflow.server.services.logging_service import LoggingService
from mini_mlflow.server.api.models import (
    LogParamRequest, LogMetricRequest, LogArtifactRequest, ArtifactResponse,
    LogTagRequest, TagResponse
)

router = APIRouter()
logging_service = LoggingService()

@router.post("/param/log")
def log_param(request: LogParamRequest):
    param = logging_service.log_param(request.run_id, request.key, request.value)
    return {
        "id": param.id,
        "run_id": param.run_id,
        "status": "OK"
    }

@router.post("/metric/log")
def log_metric(request: LogMetricRequest):
    logging_service.log_metric(request.run_id, request.key, request.value, request.step)
    return {
        "status": "ok"
    }

@router.post("/artifacts/log", response_model=ArtifactResponse)
def log_artifact(request: LogArtifactRequest):
    artifact = logging_service.log_artifact(request.run_id, request.file_path)
    return ArtifactResponse(path=artifact.path)

@router.post("/tag/log", response_model=TagResponse)
def log_tag(request: LogTagRequest):
    tag = logging_service.log_tag(request.run_id, request.key, request.value)
    return TagResponse(key=tag.key, value=tag.value)
