from typing import List, Optional
from pydantic import BaseModel, Field


class AccountBase(BaseModel):
    name: str = Field(
        default="Savings", description="name of the account", min_length=4
    )
    currency: str = Field(default="USD")
    money: float = Field(default=0)


class OrderResponse(BaseModel):
    """Schema for orders in account response"""

    id: str
    description: Optional[str]
    order_type: str
    amount: float
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class AccountWithOrders(BaseModel):
    """Schema for account with its orders"""

    id: str
    owner_id: str
    name: str
    currency: str
    money: float
    orders: List[OrderResponse] = []

    class Config:
        from_attributes = True
