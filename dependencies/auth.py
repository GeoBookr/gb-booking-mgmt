from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt

SECRET = "mocksecret"
ALGORITHM = "HS256"
auth_scheme = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        return {"user_id": payload["sub"], "role": payload["role"]}
    except Exception:
        raise HTTPException(status_code=403, detail="Invalid token")
