import uuid
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.core.security import (
    hash_password,
    authenticate_superuser_or_user,
    create_access_token,
    get_current_user,
    get_superuser_dependency,
)
from app.database.core import get_db
from app.api.users.schemas import UserBase
from app.api.users.models import Users

router = APIRouter(prefix="/user", tags=["user"])

db_dependency = Annotated[Session, Depends(get_db)]

user_dependency = Annotated[dict, Depends(get_current_user)]
superuser_dependency = Annotated[dict, Depends(get_superuser_dependency)]


"""═══ AUTHENTICATION ═══"""


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency
):
    user = authenticate_superuser_or_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    token = create_access_token({"sub": user["username"], "id": user["id"]})

    return {"access_token": token, "token_type": "bearer"}


@router.post("/register")
async def register(db: db_dependency, user_request: UserBase):
    """Register a new user account"""
    user_model = Users(
        id=uuid.uuid4(),
        username=user_request.username,
        hashed_password=hash_password(user_request.password),
    )

    db.add(user_model)
    db.commit()
    return {"Data": "User created successfully"}


"""═══ USER PROFILE ═══"""


@router.get("/profile")
async def get_profile(user: user_dependency, db: db_dependency):
    """Get current user profile"""
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return {"User": user}


"""═══ ADMIN ONLY ═══"""


@router.get("/all")
async def get_all_users(superuser: superuser_dependency, db: db_dependency):
    """Get all users - requires superuser permissions"""
    try:
        users = db.query(Users).all()
        return {"users": users, "count": len(users)}
    except Exception:
        raise HTTPException(status_code=500, detail="Error retrieving users")


@router.delete("/{user_id}")
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
    return {"total_users": total_users, "superuser": superuser.get("username")}
