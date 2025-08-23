import uuid

from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session, joinedload

from app.api.accounts.models import Accounts
from app.api.accounts.schemas import AccountBase
from app.api.orders.models import Orders
from app.database.core import get_db
from app.core.security import (
    get_current_user,
    get_superuser_dependency,
    check_resource_access,
    is_superuser,
)

router = APIRouter(prefix="/account", tags=["account"])

db_dependency = Annotated[Session, Depends(get_db)]

user_dependency = Annotated[dict, Depends(get_current_user)]
superuser_dependency = Annotated[dict, Depends(get_superuser_dependency)]

"""═══ MY ACCOUNTS ═══"""


@router.get("/")
async def get_my_accounts(db: db_dependency, user: user_dependency):
    """Returns All Accounts of active user"""
    return (
        db.query(Accounts)
        .options(joinedload(Accounts.orders))
        .filter(Accounts.owner_id == user["id"])
        .all()
    )


@router.post("/")
async def create_account(db: db_dependency, user: user_dependency, acc: AccountBase):
    """Creates an account for the active user"""
    db_acc = Accounts(
        id=uuid.uuid4(),
        owner_id=user["id"],
        name=acc.name,
        currency=acc.currency,
        money=acc.money,
    )
    db.add(db_acc)
    db.commit()
    return {"data": "Account created successfully"}


@router.get("/{account_id}")
async def get_account_by_id(
    *, db: db_dependency, user: user_dependency, account_id: str
):
    """Get account by ID"""
    db_acc = (
        db.query(Accounts)
        .options(joinedload(Accounts.orders))
        .filter(Accounts.id == account_id)
        .first()
    )
    if not db_acc:
        raise HTTPException(status_code=404, detail="Account Not Found")

    check_resource_access(user, db_acc.owner_id, "account")

    return db_acc


"""═══ USER SPECIFIC (Admin can access any) ═══"""


@router.get("/user/{user_id}")
async def get_accounts_by_user(db: db_dependency, user: user_dependency, user_id: str):
    """Returns accounts of a specific user (superuser only) or own accounts"""
    if not is_superuser(user) and user["id"] != user_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied: You can only access your own accounts",
        )

    try:
        accounts = (
            db.query(Accounts)
            .options(joinedload(Accounts.orders))
            .filter(Accounts.owner_id == user_id)
            .all()
        )
        return {"user_id": user_id, "accounts": accounts, "count": len(accounts)}
    except Exception:
        raise HTTPException(status_code=500, detail="Could not retrieve data")


"""═══ ADMIN ONLY ═══"""


@router.get("/all")
async def get_all_accounts(db: db_dependency, super_db: superuser_dependency):
    """Returns all accounts in the DB ( only superuser )"""
    return db.query(Accounts).options(joinedload(Accounts.orders)).all()


"""═══ ACCOUNT MANAGEMENT ═══"""


@router.put("/{account_id}")
async def update_account(
    account_id: str, db: db_dependency, user: user_dependency, new_acc: AccountBase
):
    """Update account information"""
    db_acc = db.query(Accounts).filter(Accounts.id == account_id).first()
    if not db_acc:
        raise HTTPException(status_code=404, detail="Account Not Found")

    if not is_superuser(user) and user["id"] != db_acc.owner_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    db_acc.name = new_acc.name
    db_acc.money = new_acc.money
    db_acc.currency = new_acc.currency
    db.add(db_acc)
    db.commit()
    db.refresh(db_acc)
    return {"data": "Account updated"}


@router.put("/reset/{account_id}")
async def reset_account(db: db_dependency, user: user_dependency, account_id: str):
    db_account = db.query(Accounts).options(joinedload(Accounts.orders)).filter(Accounts.id == account_id).first()
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    if not is_superuser(user) and user["id"] != db_account.owner_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    db_orders = db.query(Orders).filter(Orders.account_id == db_account.id).all()
    for element in db_orders:
        db.delete(element)
    db_account.money = 0
    db.commit()
    db.refresh(db_account)
    return db_account


@router.delete("/{account_id}")
async def delete_account(account_id: str, db: db_dependency, user: user_dependency):
    """Delete account"""
    db_acc = db.query(Accounts).filter(Accounts.id == account_id).first()
    if not db_acc:
        raise HTTPException(status_code=404, detail="Account doesn't exist")
    if not is_superuser(user) and user["id"] != db_acc.owner_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    db.delete(db_acc)
    db.commit()
    return {"data": "Account deleted successfully"}
