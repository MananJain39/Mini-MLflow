from fastapi import APIRouter
from typing import List
from mini_mlflow.Server.services.tracker import Tracker
from mini_mlflow.Server.DB import session as db_session
from mini_mlflow.Server.DB.models import Experiment
from mini_mlflow.Server.API.models import ExperimentRequest, ExperimentResponse

router = APIRouter()
tracker = Tracker()



@router.post("/experiments/set", response_model=ExperimentResponse)
def set_experiment(request: ExperimentRequest):
    exp = tracker.get_or_create_experiment(request.name)
    return ExperimentResponse(id=exp.id, name=exp.name, created_at=exp.created_at)

@router.get("/experiments", response_model=List[ExperimentResponse])
def list_experiment():
    db = db_session.SessionLocal()
    try:
        experiments = db.query(Experiment).all()
        return [
            ExperimentResponse(
                id=exp.id,
                name=exp.name,
                created_at=exp.created_at,
            )
            for exp in experiments
        ]
    finally:
        db.close()