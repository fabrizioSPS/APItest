from typing import Union

from pydantic import BaseModel


class Token(BaseModel):
    """
    Schema for the access token.

    Attributes:
        access_token: The access token string.
        token_type: The type of the token.
    """
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    Schema for the token data.

    Attributes:
        username: The username in the token, defaults to None.
    """
    username: Union[str, None] = None


class UserInfo(BaseModel):
    """
    Base schema for user information.

    Attributes:
        username: The username of the user.
        email: The email of the user, defaults to None.
        full_name: The full name of the user, defaults to None.
        disabled: A boolean indicating whether the user is disabled, defaults to None.
    """
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None


class UserInDB(UserInfo):
    """
    Schema for user information in the database.

    Attributes:
        hashed_password: The hashed password of the user.
    """
    hashed_password: str


class UserBase(BaseModel):
    """
    Base schema for a user.

    Attributes:
        email: The email of the user.
    """
    email: str


class UserCreate(UserBase):
    """
    Schema for creating a user.

    Attributes:
        password: The password of the user.
    """
    password: str


class User(BaseModel):
    """
    Schema for a user.

    Attributes:
        id: The ID of the user.
        username: The username of the user.
        email: The email of the user.
        full_name: The full name of the user.
        disabled: A boolean indicating whether the user is disabled.
    """
    id: int
    username: str
    email: str
    full_name: str
    disabled: bool

    class Config:
        orm_mode = True


class Item(BaseModel):
    """
    Schema for an item.

    Attributes:
        name: The name of the item.
        description: The description of the item, defaults to None.
        price: The price of the item.
        tax: The tax on the item, defaults to None.
    """
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None
    