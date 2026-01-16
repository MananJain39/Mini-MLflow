from datetime import datetime
from Server.DB.models import Experiment, Run, Param, Metric, Artifact
from Server.DB.session import SessionLocal, get_db

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
