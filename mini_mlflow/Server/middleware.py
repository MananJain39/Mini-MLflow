import uuid
import time
from starlette.middleware.base import BaseHTTPMiddleware
from mini_mlflow.Server.logger import logger

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        start_time = time.time()
        
        # We can attach the ID to the request state
        request.state.request_id = request_id
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)
        
        logger.info(f"method={request.method} path={request.url.path} status={response.status_code} "
                    f"duration={process_time:.4f} request_id={request_id}")
        
        return response
