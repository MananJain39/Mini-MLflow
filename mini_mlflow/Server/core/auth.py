import os
from fastapi import Security
from fastapi.security import APIKeyHeader

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def get_api_key(api_key_header: str = Security(api_key_header)):
    api_keys_env = os.getenv("API_KEYS", "")
    if not api_keys_env:
        # If no keys are configured, bypass auth (e.g. local MVP)
        return None
    
    valid_keys = [k.strip() for k in api_keys_env.split(",") if k.strip()]
    if api_key_header in valid_keys:
        return api_key_header
        
    from fastapi import HTTPException, status
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API Key",
    )
