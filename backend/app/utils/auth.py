from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.config import settings


security = HTTPBearer()
security_optional = HTTPBearer(auto_error=False)


def get_user_from_token_str(token_str: str, db: Session) -> User:
    try:
        payload = jwt.decode(
            token_str,
            settings.SECRET_KEY,
            algorithms=["HS256"]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        user_id = int(user_id)
    except (JWTError, TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    return get_user_from_token_str(credentials.credentials, db)
