from Server.DB.session import engine
from Server.DB import models
from Server.DB.models import Base

Base.metadata.create_all(bind=engine)
print("DB Created")
