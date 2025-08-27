from sqlalchemy import Column, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database.core import Base


class Orders(Base):
    __tablename__ = "orders"

    id = Column(String, primary_key=True, index=True)
    created_by = Column(String, ForeignKey("users.id"))
    account_id = Column(
        String, ForeignKey("accounts.id")
    )  # Nouvelle relation vers Account
    created_at = Column(String)
    updated_at = Column(String)
    description = Column(String)
    order_type = Column(String)
    amount = Column(Float)

    # Relation vers le compte
    account = relationship("Accounts", back_populates="orders")
