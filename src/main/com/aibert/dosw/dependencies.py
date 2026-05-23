from typing import Annotated
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from com.aibert.dosw.config import settings

security = HTTPBearer(auto_error=False)


def get_current_user(
    request: Request,
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(security)
    ] = None,
) -> dict:

    user_id = request.headers.get("X-User-Id")
    user_email = request.headers.get("X-User-Email")

    if user_id and user_email:
        return {
            "user_id": user_id,
            "email": user_email,
            "token": None,
            "payload": {},
        }

    # Fallback: Bearer token directo (desarrollo local)
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
        user_id = payload.get("userId") or payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing 'sub' claim",
            )
        return {
            "user_id": user_id,
            "token": credentials.credentials,
            "payload": payload,
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
