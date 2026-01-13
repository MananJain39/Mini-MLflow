import uuid
from datetime import datetime
from sqlalchemy import Column,String, DateTime, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from .session import Base

def gen_id():
    return str(uuid.uuid4())

class Experiment(Base):
    __tablename__ = "experiments"

    id = Column(String, primary_key = True, default = gen_id)
    name = Column(String, unique = True, index =True)
    created_at = Column(DateTime, default = datetime.utcnow)

    runs = relationship("Run", back_populates="experiment")

class Run(Base):
    __tablename__ = "runs"

    id = Column(String, primary_key = True, default = gen_id)
    experiment_id = Column(String, ForeignKey("experiments.id"))
    start_time = Column(DateTime, default = datetime.utcnow)
    end_time = Column(DateTime, nullable = True)

    experiment = relationship("Experiment", back_populates="runs")
    params = relationship("Param", back_populates = "run")
    artifacts = relationship("Artifact", back_populates = "run")
    metrics = relationship("Metric", back_populates = "run")


        