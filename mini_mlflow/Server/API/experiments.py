from fastapi import APIRouter
from typing import List
from mini_mlflow.server.services.experiment_service import ExperimentService
from mini_mlflow.server.api.models import ExperimentRequest, ExperimentResponse

router = APIRouter()
experiment_service = ExperimentService()

@router.post("/experiments/set", response_model=ExperimentResponse)
def set_experiment(request: ExperimentRequest):
    exp = experiment_service.get_or_create_experiment(request.name)
    return ExperimentResponse(id=exp.id, name=exp.name, created_at=exp.created_at)

@router.get("/experiments", response_model=List[ExperimentResponse])
def list_experiment():
    experiments = experiment_service.list_experiments()
    return [
        ExperimentResponse(
            id=exp.id,
            name=exp.name,
            created_at=exp.created_at,
        )
        for exp in experiments
    ]