from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer
import uuid
from datetime import datetime, timedelta
import json
from ..redis_manager import RedisManager

security = HTTPBearer()

def create_session(user_info: dict) -> str:
    session_id = str(uuid.uuid4())
    session_data = {
        "user_id": user_info["id"],
        "email": user_info["email"],
        "created_at": datetime.now().isoformat()
    }

    redis_client = RedisManager.get_client()
    redis_client.setx(
        f"session:{session_id}",
        timedelta(hours=24),
        json.dumps(session_data)
    )

    return session_id

def get_current_user(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    redis_client = RedisManager.get_client()
    session_data = redis_client.get(f"session:{session_id}")
    if not session_data:
        raise HTTPException(status_code=401, detail="Session expired")
    
    return json.loads(session_data)
