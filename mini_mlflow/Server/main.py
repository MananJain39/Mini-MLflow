from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from mini_mlflow.Server.API.experiments import router as experiments_router
from mini_mlflow.Server.API.runs import router as runs_router
from mini_mlflow.Server.API.logging import router as logging_router
from mini_mlflow.Server.health import router as health_router
from mini_mlflow.Server.middleware import RequestIDMiddleware
from mini_mlflow.Server.auth import get_api_key

app = FastAPI()

app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="")

app.include_router(
    experiments_router, 
    prefix="/api",
    dependencies=[Depends(get_api_key)]
)
app.include_router(
    runs_router, 
    prefix="/api",
    dependencies=[Depends(get_api_key)]
)
app.include_router(
    logging_router, 
    prefix="/api",
    dependencies=[Depends(get_api_key)]
)