from fastapi import APIRouter
from pydantic import BaseModel
from Server.services.tracker import Tracker
from Server.DB.session import SessionLocal
from Server.DB.models import Experiment

router = APIRouter()
tracker = Tracker()


class ExperimentRequest(BaseModel):
    name: str


@router.post("/experiments/set")
def set_experiment(request: ExperimentRequest):
    exp = tracker.get_or_create_experiment(request.name)
    return {"id": exp.id, "name": exp.name, "created_at": exp.created_at}

@router.get("/experiments")
def list_experiment():
    db = SessionLocal()
    try:
        experiments = db.query(Experiment).all()
        return [
            {
                "id": exp.id,
                "name": exp.name,
                "created_at": exp.created_at,
            }
            for exp in experiments
        ]
    finally:
        db.close()