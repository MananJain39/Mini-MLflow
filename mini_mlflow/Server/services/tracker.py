from datetime import datetime, timezone
from Server.DB.models import Experiment, Run, Param, Metric, Artifact
from Server.DB.session import SessionLocal
import os
import shutil

class Tracker:

    def get_or_create_experiment(self, name: str):
        db = SessionLocal() # create a new session
        try:
            exp = db.query(Experiment).filter_by(name = name).first()
            if exp:
                return exp

            exp = Experiment(name=name)
            db.add(exp) 
            db.commit() #INSERT
            db.refresh(exp)
            return exp
        finally:
            db.close()

    def start_run(self, experiment_id:str):
        db = SessionLocal()
        run = Run(experiment_id = experiment_id)
        db.add(run)
        db.commit()
        db.refresh(run)
        db.close()
        return run
    
    def end_run(self, run_id:str):
        db = SessionLocal()
        run = db.get(Run, run_id)
        if not run:
            raise ValueError(f"Run not found: {run_id}")
        run.end_time = datetime.now(timezone.utc)
        run.status = "FINISHED"
        db.commit()
        db.refresh(run)
        db.close()
        return run

    def log_param(self, run_id:str, key:str, value:str):
        db = SessionLocal()

        run = db.get(Run, run_id)
        if not run:
            raise ValueError(f"Run not found: {run_id}")
        
        param = Param(run_id = run_id, key = key, value = str(value))
        db.add(param)
        db.commit()
        db.refresh(param)
        db.close()
        return param

    def log_metric(self, run_id:str, key:str, value:float, step: int = 0):
        db = SessionLocal()
        
        run = db.get(Run, run_id)
        if not run:
            raise ValueError(f"Run not found: {run_id} ")
        
        metric = Metric(run_id = run_id, key = key, value = float(value), step = step)
        db.add(metric)
        db.commit()
        db.refresh(metric)
        db.close()
        return metric

    ARTIFACT_ROOT = "storage/artifacts"
    def log_artifact(self, run_id: str, file_path: str):
        db = SessionLocal()
        run = db.get(Run, run_id)
        if not run:
            raise ValueError(f"Run not found: {run_id}")
        
        run_dir = os.path.join(self.ARTIFACT_ROOT, run_id)
        os.makedirs(run_dir, exist_ok=True)

        filename = os.path.basename(file_path)
        dest = os.path.join(run_dir, filename)

        if not os.path.isfile(file_path):
            raise ValueError(f"File not found: {file_path}")

        shutil.copy(file_path, dest)

        artifact = Artifact(run_id=run_id, path=dest)
        db.add(artifact)
        db.commit()
        db.refresh(artifact)
        db.close()
        return artifact
