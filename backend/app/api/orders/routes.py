import uuid

from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.orders.schemas import OrderBase
from api.orders.models import Orders
from api.accounts.models import Accounts
from database.core import get_db
from core.security import get_current_user, get_superuser_dependency, is_superuser

router = APIRouter(prefix="/order", tags=["order"])

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
superuser_dependency = Annotated[dict, Depends(get_superuser_dependency)]

"""═══ MY ORDERS ═══"""


@router.get("/")
async def get_my_orders(db: db_dependency, user: user_dependency):
    """Get all orders of current user"""
    return db.query(Orders).filter(Orders.created_by == user["id"]).all()


@router.post("/")
async def create_order(db: db_dependency, user: user_dependency, order: OrderBase):
    """Create a new order"""
    db_order = Orders(
        id=uuid.uuid4(),
        created_by=user["id"],
        created_at=datetime.now(),
        updated_at="",
        account_id=order.account_id,
        description=order.description,
        order_type=order.order_type,
        amount=order.amount,
    )
    db_account = db.query(Accounts).filter(Accounts.id == db_order.account_id).first()
    db_account.money += db_order.amount
    db.add(db_account)
    db.add(db_order)
    db.commit()
    return {"data": "Order created successfully"}


@router.get("/{order_id}")
async def get_order_by_id(db: db_dependency, user: user_dependency, order_id: str):
    """Get order by ID"""
    db_order = db.query(Orders).filter(Orders.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order does not exist")
    if not is_superuser(user) and user["id"] != db_order.created_by:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return db_order


"""═══ ORDER MANAGEMENT ═══"""


@router.put("/{order_id}")
async def update_order(
    db: db_dependency, user: user_dependency, order_id: str, new_order: OrderBase
):
    """Update order information"""
    db_order = db.query(Orders).filter(Orders.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    if not is_superuser(user) and user["id"] != db_order.created_by:
        raise HTTPException(status_code=401, detail="Unauthorized")

    db_order.updated_at = datetime.now()
    db_order.description = new_order.description
    db_order.order_type = new_order.order_type
    db_order.amount = new_order.amount
    db_order.account_id = new_order.account_id

    db.commit()
    db.refresh(db_order)

    return db_order


@router.delete("/{order_id}")
async def delete_order(db: db_dependency, user: user_dependency, order_id: str):
    """Delete order"""
    db_order = db.query(Orders).filter(Orders.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order does not exist")
    if not is_superuser(user) and user["id"] != db_order.created_by:
        raise HTTPException(status_code=401, detail="Unauthorized")

    db.delete(db_order)
    db.commit()
    return {"data": "Order deleted successfully"}


"""═══ ACCOUNT RELATED ═══"""


@router.get("/account/{account_id}")
async def get_orders_by_account(
    db: db_dependency, user: user_dependency, account_id: str
):
    """Get all orders for a specific account"""
    # Verify account access first
    from api.accounts.models import Accounts
    from core.security import check_resource_access

    account = db.query(Accounts).filter(Accounts.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    check_resource_access(user, account.owner_id, "account")

    orders = db.query(Orders).filter(Orders.account_id == account_id).all()
    return {"account_id": account_id, "orders": orders, "count": len(orders)}


"""═══ ADMIN ONLY ═══"""


@router.get("/all")
async def get_all_orders(db: db_dependency, superuser: superuser_dependency):
    """Get all orders in the system (admin only)"""
    return db.query(Orders).all()
