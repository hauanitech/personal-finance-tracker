from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class OrderType(Enum):
    EXPENSE = "Expense"
    ADD = "Add"


class OrderBase(BaseModel):
    account_id: str = Field(description="ID of the account this order belongs to")
    description: Optional[str] = Field(default="", max_length=100)
    order_type: str
    amount: float = Field(default=0)
