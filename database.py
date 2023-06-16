from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./sqlite3.db"
# add acount with:
# INSERT INTO users VALUES (1, 'johndoe', 'johndoe@example.com', 'John Doe', false, '$2b$12$dQD2AD2Y.Aa8F3IliHPfk.yNESW7FZe3RmeT38K661sg/vds404ga');
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

Base = declarative_base()


async def get_db():
    session = AsyncSession(engine)
    try:
        yield session
    finally:
        await session.close()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String, index=True)
    disabled = Column(Boolean, default=False)
    hashed_password = Column(String)
