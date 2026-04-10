from mini_mlflow.server.db.session import engine
from mini_mlflow.server.db import models
from mini_mlflow.server.db.models import Base

Base.metadata.create_all(bind=engine)
print("DB Created")
