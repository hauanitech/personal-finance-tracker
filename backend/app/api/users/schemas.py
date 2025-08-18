from pydantic import BaseModel, Field


class UserBase(BaseModel):
    username: str = Field(min_length=5, max_length=20, default="username")
    password: str = Field(min_length=8, max_length=100, default="password")
