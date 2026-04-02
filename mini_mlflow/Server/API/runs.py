from fastapi import APIRouter, Query
from typing import List
from mini_mlflow.Server.services.tracker import Tracker
from mini_mlflow.Server.DB.models import Run, Param, Metric, Artifact, Tag
from mini_mlflow.Server.DB import session as db_session
from mini_mlflow.Server.API.models import (
    StartRunRequest, EndRunRequest, RunResponse, 
    RunListResponse, RunDetailsResponse
)

router = APIRouter()
tracker = Tracker()



@router.post("/run/start", response_model=RunResponse)
def start_run(request: StartRunRequest):
    run = tracker.start_run(request.experiment_id)
    return RunResponse(
        id=run.id,
        experiment_id=run.experiment_id,
        start_time=run.start_time,
        status=run.status,
    )



@router.post("/run/end", response_model=RunResponse)
def end_run(request: EndRunRequest):
    run = tracker.end_run(request.run_id)
    return RunResponse(
        id=run.id, 
        experiment_id=run.experiment_id,
        start_time=run.start_time,
        end_time=run.end_time, 
        status=run.status
    )


@router.get("/experiments/{experiment_id}/runs", response_model=List[RunListResponse])
def list_runs(
    experiment_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    status: str = None
):
    db = db_session.SessionLocal()
    try:
        query = db.query(Run).filter_by(experiment_id=experiment_id)
        if status:
            query = query.filter_by(status=status)
        runs = query.offset(skip).limit(limit).all()
        return [
            RunListResponse(
                run_id=run.id,
                status=run.status,
                start_time=run.start_time,
                end_time=run.end_time,
            )
            for run in runs
        ]
    finally:
        db.close()


@router.get("/runs/{run_id}", response_model=RunDetailsResponse)
def get_details(run_id: str):
    db = db_session.SessionLocal()
    try:
        params = db.query(Param).filter_by(run_id=run_id).all()
        metrics = db.query(Metric).filter_by(run_id=run_id).all()
        artifacts = db.query(Artifact).filter_by(run_id=run_id).all()
        tags = db.query(Tag).filter_by(run_id=run_id).all()

        return RunDetailsResponse(
            run_id=run_id,
            params=[{"key": p.key, "value": p.value} for p in params],
            metrics=[{"key": m.key, "value": m.value, "step": m.step} for m in metrics],
            artifacts=[{"path": a.path} for a in artifacts],
            tags=[{"key": t.key, "value": t.value} for t in tags]
        )
    finally:
        db.close()
