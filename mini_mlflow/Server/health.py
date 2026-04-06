from fastapi import APIRouter
from mini_mlflow.Server.DB import session as db_session
from sqlalchemy import text

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.get("/ready")
def readiness_check():
    db = db_session.SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="Database not ready")
    finally:
        db.close()
