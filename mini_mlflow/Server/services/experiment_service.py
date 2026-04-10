from mini_mlflow.server.db.models import Experiment
from mini_mlflow.server.db import session as db_session

class ExperimentService:
    def get_or_create_experiment(self, name: str) -> Experiment:
        db = db_session.SessionLocal()
        try:
            exp = db.query(Experiment).filter_by(name=name).first()
            if exp:
                return exp

            exp = Experiment(name=name)
            db.add(exp)
            db.commit()
            db.refresh(exp)
            return exp
        finally:
            db.close()

    def list_experiments(self) -> list[Experiment]:
        db = db_session.SessionLocal()
        try:
            return db.query(Experiment).all()
        finally:
            db.close()
