from mini_mlflow.server.db.models import Run, Param, Metric, Artifact, Tag
from mini_mlflow.server.db import session as db_session
from mini_mlflow.server.storage.local import LocalStorage

class LoggingService:
    def __init__(self, storage_backend=None):
        self.storage = storage_backend or LocalStorage()

    def log_param(self, run_id: str, key: str, value: str) -> Param:
        db = db_session.SessionLocal()
        try:
            run = db.get(Run, run_id)
            if not run:
                raise ValueError(f"Run not found: {run_id}")
            
            param = Param(run_id=run_id, key=key, value=str(value))
            db.add(param)
            db.commit()
            db.refresh(param)
            return param
        finally:
            db.close()

    def log_metric(self, run_id: str, key: str, value: float, step: int = 0) -> Metric:
        db = db_session.SessionLocal()
        try:
            run = db.get(Run, run_id)
            if not run:
                raise ValueError(f"Run not found: {run_id}")
            
            metric = Metric(run_id=run_id, key=key, value=float(value), step=step)
            db.add(metric)
            db.commit()
            db.refresh(metric)
            return metric
        finally:
            db.close()

    def log_artifact(self, run_id: str, file_path: str) -> Artifact:
        db = db_session.SessionLocal()
        try:
            run = db.get(Run, run_id)
            if not run:
                raise ValueError(f"Run not found: {run_id}")
            
            # Use storage backend
            dest_path = self.storage.log_artifact(run_id, file_path)

            artifact = Artifact(run_id=run_id, path=dest_path)
            db.add(artifact)
            db.commit()
            db.refresh(artifact)
            return artifact
        finally:
            db.close()

    def log_tag(self, run_id: str, key: str, value: str) -> Tag:
        db = db_session.SessionLocal()
        try:
            run = db.get(Run, run_id)
            if not run:
                raise ValueError(f"Run not found: {run_id}")
            tag = Tag(run_id=run_id, key=key, value=str(value))
            db.add(tag)
            db.commit()
            db.refresh(tag)
            return tag
        finally:
            db.close()
