from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# --- Requests ---
class StartRunRequest(BaseModel):
    experiment_id: str

class EndRunRequest(BaseModel):
    run_id: str

class ExperimentRequest(BaseModel):
    name: str

class LogParamRequest(BaseModel):
    run_id: str
    key: str
    value: str

class LogMetricRequest(BaseModel):
    run_id: str
    key: str
    value: float
    step: int = 0

class LogArtifactRequest(BaseModel):
    run_id: str
    file_path: str

class LogTagRequest(BaseModel):
    run_id: str
    key: str
    value: str

# --- Responses ---
class RunResponse(BaseModel):
    id: str
    experiment_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str

class RunListResponse(BaseModel):
    run_id: str
    status: str
    start_time: datetime
    end_time: Optional[datetime] = None

class ExperimentResponse(BaseModel):
    id: str
    name: str
    created_at: datetime

class ParamResponse(BaseModel):
    key: str
    value: str

class MetricResponse(BaseModel):
    key: str
    value: float
    step: int

class ArtifactResponse(BaseModel):
    path: str

class TagResponse(BaseModel):
    key: str
    value: str

class RunDetailsResponse(BaseModel):
    run_id: str
    params: List[ParamResponse]
    metrics: List[MetricResponse]
    artifacts: List[ArtifactResponse]
    tags: List[TagResponse]
