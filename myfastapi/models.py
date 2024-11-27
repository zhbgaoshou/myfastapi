from sqlmodel import SQLModel, Field
from pydantic import EmailStr
from datetime import datetime


class UserBase(SQLModel):
    username: str = Field(index=True)
    email: EmailStr | None = None
    avatar: str | None = None


class UserCreate(UserBase):
    password: str = Field(min_length=6)


class UserUpdate(UserBase):
    password: str | None = None
    username: str | None = None
    is_active: bool | None = None


class UserOut(UserBase):
    id: int
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    last_login: datetime | None = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S"),
        }


class User(UserBase, table=True):
    __tablename__ = "users"
    id: int | None = Field(default=None, primary_key=True)
    password: str
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    last_login: datetime | None = None
