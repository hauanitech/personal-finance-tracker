from sqlalchemy import Column, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database.core import Base


class Accounts(Base):
    __tablename__ = "accounts"

    id = Column(String, primary_key=True, index=True)
    owner_id = Column(String, ForeignKey("users.id"))
    name = Column(String)
    currency = Column(String)
    money = Column(Float)

    # Relation vers les ordres
    orders = relationship(
        "Orders", back_populates="account", cascade="all, delete-orphan"
    )
