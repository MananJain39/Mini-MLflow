import uuid
from datetime import datetime
from sqlalchemy import Column,String, DateTime, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from .session import Base

def gen_id():
    return str(uuid.uuid4())

class Experiment(Base):
    __tablename__ = "experiments"

    id = Column(String, primary_key = True, default = gen_id)  #UUID as string
    name = Column(String, unique = True, index =True)
    created_at = Column(DateTime, default = datetime.utcnow)

    runs = relationship("Run", back_populates="experiment")

class Run(Base):
    __tablename__ = "runs"

    id = Column(String, primary_key = True, default = gen_id)
    experiment_id = Column(String, ForeignKey("experiments.id"))
    start_time = Column(DateTime, default = datetime.utcnow)
    end_time = Column(DateTime, nullable = True)
    status = Column(String, default = "RUNNING")

    experiment = relationship("Experiment", back_populates="runs")
    params = relationship("Param", back_populates = "run")
    artifacts = relationship("Artifact", back_populates = "run")
    metrics = relationship("Metric", back_populates = "run")

class Param(Base):
    __tablename__ = "params"
    id = Column(Integer, primary_key = True, autoincrement=True)
    run_id = Column(String, ForeignKey("runs.id"))
    key = Column(String)
    value = Column(String)

    run = relationship("Run", back_populates="params")

class Metric(Base):
    __tablename__ = "metrics"
    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String, ForeignKey("runs.id"))
    key = Column(String)
    value = Column(Float)
    step = Column(Integer)

    run = relationship("Run", back_populates="metrics")

class Artifact(Base):
    __tablename__ = "artifacts"
    id = Column(Integer, primary_key = True, autoincrement=True)
    run_id = Column(String, ForeignKey ("runs.id"))
    path = Column(String)
    
    run = relationship("Run", back_populates="artifacts")

        