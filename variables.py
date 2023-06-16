"""
Author: Enrico Schmitz
API
Script: 
"""
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./sqlite3.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, echo=True
)

Base = declarative_base()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "66d5528fbd7adc9cb5446d6a37e2c5fce851beeb78e0cbd3017b9f8b00434dc3"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
