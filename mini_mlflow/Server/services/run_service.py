from datetime import datetime, timezone
from typing import Dict, Any, List
from mini_mlflow.server.db.models import Run, Param, Metric, Artifact, Tag
from mini_mlflow.server.db import session as db_session

class RunService:
    def start_run(self, experiment_id: str) -> Run:
        db = db_session.SessionLocal()
        try:
            run = Run(experiment_id=experiment_id)
            db.add(run)
            db.commit()
            db.refresh(run)
            return run
        finally:
            db.close()
    
    def end_run(self, run_id: str) -> Run:
        db = db_session.SessionLocal()
        try:
            run = db.get(Run, run_id)
            if not run:
                raise ValueError(f"Run not found: {run_id}")
            run.end_time = datetime.now(timezone.utc)
            run.status = "FINISHED"
            db.commit()
            db.refresh(run)
            return run
        finally:
            db.close()

    def list_runs(self, experiment_id: str, skip: int = 0, limit: int = 100, status: str = None) -> List[Run]:
        db = db_session.SessionLocal()
        try:
            query = db.query(Run).filter_by(experiment_id=experiment_id)
            if status:
                query = query.filter_by(status=status)
            return query.offset(skip).limit(limit).all()
        finally:
            db.close()

    def get_run_details(self, run_id: str) -> Dict[str, Any]:
        """Returns details of a run including params, metrics, artifacts, and tags."""
        db = db_session.SessionLocal()
        try:
            params = db.query(Param).filter_by(run_id=run_id).all()
            metrics = db.query(Metric).filter_by(run_id=run_id).all()
            artifacts = db.query(Artifact).filter_by(run_id=run_id).all()
            tags = db.query(Tag).filter_by(run_id=run_id).all()

            return {
                "run_id": run_id,
                "params": [{"key": p.key, "value": p.value} for p in params],
                "metrics": [{"key": m.key, "value": m.value, "step": m.step} for m in metrics],
                "artifacts": [{"path": a.path} for a in artifacts],
                "tags": [{"key": t.key, "value": t.value} for t in tags]
            }
        finally:
            db.close()
