from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
from config import settings

SECRET = settings.JWT_SECRET
ALGORITHM = settings.JWT_ALGORITHM
auth_scheme = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    token = credentials.credentials
    try:
        print(f"Decoding token: {token}")
        print(f"Decoding with secret: {SECRET}")
        print(f"Decoding with algorithm: {ALGORITHM}")

        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        return {"user_id": payload["sub"]}
    except Exception:
        raise HTTPException(status_code=403, detail="Invalid token")
