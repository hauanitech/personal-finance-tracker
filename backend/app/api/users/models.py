from sqlalchemy import Column, String
from app.database.core import Base


class Users(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True)
    hashed_password = Column(String)
