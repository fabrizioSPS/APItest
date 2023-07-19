from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./sqlite3.db"
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

Base = declarative_base()


async def get_db():
    """
    Get a database session.

    This function is a context manager. It yields a database session and ensures
    the session is closed when exiting the context.

    Yields:
        AsyncSession: The database session.
    """
    session = AsyncSession(engine)
    try:
        yield session
    finally:
        await session.close()


class User(Base):
    """
    The User model.

    Attributes:
        id: The ID of the user. This field is the primary key.
        username: The username of the user. This field is unique.
        email: The email of the user. This field is unique.
        full_name: The full name of the user.
        disabled: A boolean indicating whether the user is disabled.
        hashed_password: The hashed password of the user.
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String, index=True)
    disabled = Column(Boolean, default=False)
    hashed_password = Column(String)
