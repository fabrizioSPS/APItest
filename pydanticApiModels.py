from typing import Union

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None


class UserInfo(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None


class UserInDB(UserInfo):
    hashed_password: str


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    disabled: bool

    class Config:
        orm_mode = True


class Item(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None
