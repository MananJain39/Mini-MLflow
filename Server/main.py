from fastapi import FastAPI
from Server.API.experiments import router as experiments_router
from Server.API.runs import router as runs_router

app = FastAPI()

app.include_router(experiments_router, prefix="/api")
app.include_router(runs_router, prefix = "/api")