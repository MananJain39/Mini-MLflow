from mini_mlflow.Server.DB.session import engine
from mini_mlflow.Server.DB import models
from mini_mlflow.Server.DB.models import Base

Base.metadata.create_all(bind=engine)
print("DB Created")
