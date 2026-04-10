from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from mini_mlflow.server.api.experiments import router as experiments_router
from mini_mlflow.server.api.runs import router as runs_router
from mini_mlflow.server.api.logging import router as logging_router
from mini_mlflow.server.core.health import router as health_router
from mini_mlflow.server.core.middleware import RequestIDMiddleware
from mini_mlflow.server.core.auth import get_api_key

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