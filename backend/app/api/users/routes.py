import uuid
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from core.security import (
    hash_password,
    authenticate_user,
    create_access_token,
    get_current_user,
)
from database.core import get_db
from api.users.schemas import UserBase
from api.users.models import Users

router = APIRouter(prefix="/user", tags=["user"])

db_depedency = Annotated[Session, Depends(get_db)]

user_dependency = Annotated[dict, Depends(get_current_user)]


@router.post("/create_user_request")
async def create_user_request(db: db_depedency, user_request: UserBase):
    user_model = Users(
        id=uuid.uuid4(),
        username=user_request.username,
        hashed_password=hash_password(user_request.password),
    )

    db.add(user_model)
    db.commit()


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_depedency
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    token = create_access_token({"sub": user.username, "id": str(user.id)})

    return {"access_token": token, "token_type": "bearer"}


@router.get("/get_user")
async def get_user(user: user_dependency, db: db_depedency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return {"User": user}
