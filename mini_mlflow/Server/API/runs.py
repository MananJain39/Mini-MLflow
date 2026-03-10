from fastapi import APIRouter
from pydantic import BaseModel
from Server.services.tracker import Tracker
from Server.DB.models import Run, Param, Metric, Artifact
from Server.DB.session import SessionLocal

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
        "status": run.status,
    }


class EndRunRequest(BaseModel):
    run_id: str


@router.post("/run/end")
def end_run(request: EndRunRequest):
    run = tracker.end_run(request.run_id)
    return {"id": run.id, "end_time": run.end_time, "status": run.status}


@router.get("/experiments/{experiments_id}/runs")
def list_runs(experiment_id: str):
    db = SessionLocal()
    runs = db.query(Run).filter_by(experiment_id=experiment_id).all()
    db.close()

    return {
        {
            "run_id": run.id,
            "status": run.status,
            "start_time": run.start_time,
            "end_time": run.end_time,
        }
        for run in runs
    }


@router.get("/runs/{run_id}")
def get_details(run_id: str):
    db = SessionLocal()
    params = db.query(Param).filer_by(run_id=run_id).all()
    metrics = db.query(Metric).filer_by(run_id=run_id).all()
    artifacts = db.query(Artifact).filer_by(run_id=run_id).all()

    db.close()

    return {
        "run_id": run_id,
        "params": [{"key": p.key, "value": p.value} for p in params],
        "metrics": [{"key": m.key, "vlaue": m.value, "step": m.step} for m in metrics],
        "artifacts": [{"path": a.path} for a in artifacts],
    }
