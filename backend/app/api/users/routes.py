import uuid
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.core.security import (
    hash_password,
    authenticate_user,
    authenticate_superuser_or_user,
    create_access_token,
    get_current_user,
    check_superuser,
    get_superuser_dependency,
)
from app.database.core import get_db
from app.api.users.schemas import UserBase
from app.api.users.models import Users

router = APIRouter(prefix="/user", tags=["user"])

db_dependency = Annotated[Session, Depends(get_db)]

user_dependency = Annotated[dict, Depends(get_current_user)]
superuser_dependency = Annotated[dict, Depends(get_superuser_dependency)]


@router.post("/create_user_request")
async def create_user_request(db: db_dependency, user_request: UserBase):
    user_model = Users(
        id=uuid.uuid4(),
        username=user_request.username,
        hashed_password=hash_password(user_request.password),
    )

    db.add(user_model)
    db.commit()
    return {"Data" : "User created successfully"}


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency
):
    user = authenticate_superuser_or_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    token = create_access_token({"sub": user["username"], "id": user["id"]})

    return {"access_token": token, "token_type": "bearer"}


@router.get("/get_user")
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return {"User": user}


@router.get("/get_all_users")
async def get_all_users(superuser: superuser_dependency, db: db_dependency):
    """Get all users - requires superuser permissions"""
    try:
        users = db.query(Users).all()
        return {"users": users, "count": len(users)}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error retrieving users")


@router.delete("/delete_user/{user_id}")
async def delete_user(user_id: str, superuser: superuser_dependency, db: db_dependency):
    """Delete a user by ID - requires superuser permissions"""
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return {"message": f"User {user.username} deleted successfully"}


@router.get("/admin/stats")
async def get_admin_stats(superuser: superuser_dependency, db: db_dependency):
    """Get admin statistics - requires superuser permissions"""
    total_users = db.query(Users).count()
    return {
        "total_users": total_users,
        "superuser": superuser.get("username")
    }