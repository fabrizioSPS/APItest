"""
Author: Enrico Schmitz
API
Script: 
"""
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

# The URL to the SQLite database.
# This can be changed to a different type of database by changing the prefix and path.
SQLALCHEMY_DATABASE_URL = "sqlite:///./sqlite3.db"

# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

# An engine that stores the connection to the database.
# The engine is created by using the database URL and passing additional connection arguments.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, echo=True
)

# The base class for all models.
# This is required by SQLAlchemy and is used to create new models.
Base = declarative_base()

# An instance of CryptContext that provides a suite of password hashing utilities.
# This is used to securely store and verify passwords.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# The secret key that's used for encoding and decoding JWT tokens.
SECRET_KEY = "66d5528fbd7adc9cb5446d6a37e2c5fce851beeb78e0cbd3017b9f8b00434dc3"

# The algorithm that's used for encoding and decoding JWT tokens.
ALGORITHM = "HS256"

# The number of minutes after which a JWT token will expire.
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# The OAuth2 password bearer instance.
# This is used to secure endpoints with OAuth2.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")