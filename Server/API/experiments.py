from fastapi import APIRouter
from pydantic import BaseModel
from Server.services.tracker import Tracker

router = APIRouter()
tracker = Tracker()


class ExperimentRequest(BaseModel):
    name: str


@router.post("/experiments/set")
def set_experiment(request: ExperimentRequest):
    exp = tracker.get_or_create_experiment(request.name)
    return {"id": exp.id, "name": exp.name, "created_at": exp.created_at}
