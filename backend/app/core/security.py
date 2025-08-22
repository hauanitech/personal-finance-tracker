from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import settings
from app.api.users.models import Users

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="api/user/token")


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str):
    return pwd_context.verify(password, hashed_password)


def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()

    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def authenticate_superuser_or_user(username: str, password: str, db):
    """Authenticate either superuser or regular user"""
    # Check if it's superuser first
    if username == settings.SUPERUSER_USERNAME and password == settings.SUPERUSER_PASSWORD:
        return {"username": username, "id": "superuser", "is_superuser": True}
    
    # Otherwise, authenticate regular user
    user = authenticate_user(username, password, db)
    if user:
        return {"username": user.username, "id": str(user.id), "is_superuser": False}
    
    return False


def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
        username: str = payload.get("sub")
        user_id: str = payload.get("id")
        if username is None or user_id is None:
            raise HTTPException(status_code=401, detail="Could not validate user")

        return {"username": username, "id": user_id}
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate user")


def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=30)):
    encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    encode.update({"exp": expire})
    return jwt.encode(encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def check_superuser(username: str, password: str):
    if username != settings.SUPERUSER_USERNAME:
        raise HTTPException(status_code=401, detail="incorrect username")
    if password != settings.SUPERUSER_PASSWORD:
        raise HTTPException(status_code=401, detail="incorrect password")
    return {"data": "welcome back superman"}


def get_superuser_dependency(current_user: Annotated[dict, Depends(get_current_user)]):
    """Dependency to check if current user is superuser"""
    if current_user.get("username") != settings.SUPERUSER_USERNAME:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return current_user