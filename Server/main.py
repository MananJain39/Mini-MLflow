from fastapi import FastAPI
from Server.API.experiments import router as experiments_router

app = FastAPI()

app.include_router(experiments_router, prefix="/api")