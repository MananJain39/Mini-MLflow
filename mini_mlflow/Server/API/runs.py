from fastapi import APIRouter, Query
from typing import List
from mini_mlflow.server.services.run_service import RunService
from mini_mlflow.server.api.models import (
    StartRunRequest, EndRunRequest, RunResponse, 
    RunListResponse, RunDetailsResponse
)

router = APIRouter()
run_service = RunService()

@router.post("/run/start", response_model=RunResponse)
def start_run(request: StartRunRequest):
    run = run_service.start_run(request.experiment_id)
    return RunResponse(
        id=run.id,
        experiment_id=run.experiment_id,
        start_time=run.start_time,
        status=run.status,
    )

@router.post("/run/end", response_model=RunResponse)
def end_run(request: EndRunRequest):
    run = run_service.end_run(request.run_id)
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
    runs = run_service.list_runs(experiment_id, skip, limit, status)
    return [
        RunListResponse(
            run_id=run.id,
            status=run.status,
            start_time=run.start_time,
            end_time=run.end_time,
        )
        for run in runs
    ]

@router.get("/runs/{run_id}", response_model=RunDetailsResponse)
def get_details(run_id: str):
    details = run_service.get_run_details(run_id)
    return RunDetailsResponse(
        run_id=details["run_id"],
        params=details["params"],
        metrics=details["metrics"],
        artifacts=details["artifacts"],
        tags=details["tags"]
    )
