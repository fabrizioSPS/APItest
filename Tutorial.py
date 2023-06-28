import json
import time
from datetime import datetime, timedelta
from typing import Annotated, List
from typing import Optional

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi import Request, Path, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import PlainTextResponse
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Import local database settings and models
import database
from InternalCode.Application.useCApp import sum_of_numbers

# Import custom JSON parser
from InternalCode.json_parser import parse_Json

# Import Pydantic models for API validation and serialization
from pydanticApiModels import Item, User, Token, TokenData

# Import slowapi for Rate Limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware


# Secret key for encoding and decoding JWT tokens. Should be a random string that is kept secure.
# To get a string like this run: openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"

# Algorithm used for encoding and decoding JWT tokens
ALGORITHM = "HS256"

# Expiration time (in minutes) for JWT tokens
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# CryptContext instance for hashing passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme instance for getting bearer token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# FastAPI application instance
app = FastAPI()

# set up the limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# add the middleware to the application
app.add_middleware(SlowAPIMiddleware)

app.add_exception_handler(HTTPException, _rate_limit_exceeded_handler)



"""
Authentication
"""

@app.on_event("startup")
async def start_db():
    """
    Event handler that is invoked when the server is starting up.
    This function will establish a connection to the database and create all tables.
    """
    async with database.engine.begin() as conn:
        await conn.run_sync(database.Base.metadata.create_all)


def verify_password(plain_password, hashed_password):
    """
    Verify a password against a hashed password using the passlib context.
    
    Args:
        plain_password: The plain-text password to check.
        hashed_password: The hashed password to check against.
        
    Returns:
        bool: True if the passwords match, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """
    Hash a password using the passlib context.
    
    Args:
        password: The plain-text password to hash.
        
    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(password)


async def get_user(db: AsyncSession, username: str) -> database.User:
    """
    Fetch a user from the database by username.
    
    Args:
        db: Database session.
        username: The username of the user to fetch.
        
    Returns:
        User: The fetched User object or None if no user was found.
    """
    result = await db.execute(select(database.User).filter_by(username=username))
    return result.scalars().first()


async def authenticate_user(db: AsyncSession, username: str, password: str) -> database.User:
    """
    Authenticate a user using their username and password.
    
    Args:
        db: Database session.
        username: The username of the user to authenticate.
        password: The password of the user to authenticate.
        
    Returns:
        User: The authenticated User object or False if authentication failed.
    """
    user = await get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a JWT access token.
    
    Args:
        data: The data to include in the token.
        expires_delta: The duration that the token will be valid for. Defaults to 15 minutes.
        
    Returns:
        str: The encoded JWT token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(db: AsyncSession = Depends(database.get_db),
                           token: str = Depends(oauth2_scheme)) -> database.User:
    """
    Function to get the current authenticated user from the database.
    This function uses a JWT token to authenticate and fetch the user.

    Args:
        db: Database session.
        token: The JWT token used for authentication.

    Returns:
        User: The authenticated User object.

    Raises:
        HTTPException: If the token is invalid or the user does not exist.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> database.User:
    """
    Function to get the current active user.
    This function checks if the authenticated user is active or not.

    Args:
        current_user: The authenticated User object.

    Returns:
        User: The authenticated User object.

    Raises:
        HTTPException: If the user is not active.
    """
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# apply the limiter to relevant endpoints
@app.post("/token", response_model=Token)
@limiter.limit("10/minute")
async def login_for_access_token(
        request: Request,
        db: AsyncSession = Depends(database.get_db),
        form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Endpoint to authenticate a user and provide an access token.
    The user needs to provide their username and password for authentication.

    Args:
        db: Database session.
        form_data: Form data with username and password.

    Returns:
        Token: The access token for the authenticated user.

    Raises:
        HTTPException: If the authentication fails.
    """
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}



@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    Endpoint to get the details of the current authenticated user.

    Args:
        current_user: The authenticated User object.

    Returns:
        User: The authenticated User object.
    """
    return current_user


@app.get("/")
async def StartPage():
    """
    Endpoint to render the start page.
    This page includes forms for login and registration.

    Returns:
        HTMLResponse: The HTML content of the start page.
    """
    content = """
    <body>
    <form action="/sum/" enctype="multipart/form-data" method="post">
    <input name="a" type="string">
    <input name="b" type="string">
    <input type="submit">
    </form>
    </body>
    """
    return HTMLResponse(content=content)


"""
Reading and loading in JSON files.
"""

@app.post("/uploadfiles/", dependencies=[Depends(oauth2_scheme)])
@limiter.limit("10/minute")  # adjust the rate limit as needed
async def create_upload_files(
        request: Request,
        files: Annotated[
            List[UploadFile], File(description="Multiple files as UploadFile")
        ],
):
    """
    Endpoint to upload multiple files.
    The first file in the list is parsed as a JSON file.

    Args:
        files: List of uploaded files.

    Returns:
        dict: The parsed JSON data.
    """
    json_file = files[0].file
    json_file.seek(0)
    json_data = json.load(json_file)
    Parsed_input = parse_Json(json_data)
    return Parsed_input



@app.get("/read_json/", dependencies=[Depends(oauth2_scheme)])
async def read_json():
    """
    Endpoint to render a page for uploading JSON files.

    Returns:
        HTMLResponse: The HTML content of the upload page.
    """
    content = """
    <body>
    <form action="/uploadfiles/" enctype="multipart/form-data" method="post">
    <input name="files" type="file" multiple>
    <input type="submit">
    </form>
    </body>
    """
    return HTMLResponse(content=content)


@app.get("/download_json/")
async def main():
    """
    Endpoint to download a JSON file named "example.json".

    Returns:
        FileResponse: The JSON file.
    """
    return FileResponse("example.json", media_type="json", filename="Api.json")

@app.post("/sum/")
async def sum(a: int, b: int):
    """
    Sum two numbers

    Returns: sum

    """
    return sum_of_numbers(a, b)

"""
Extra tutorial steps that might become useful
"""

@app.get("/items/int/{item_id}")
async def read_int(
        item_id: Annotated[int, Path(title="The ID of the item to get", gt=0, le=1000)],
        q: str,
):
    """
    Get an item by its ID.

    Args:
        item_id: The ID of the item.
        q: A query string.

    Returns:
        dict: The item information and query string.
    """
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results


@app.put("/items/multiplebodies/{item_id}")
async def update_item(item_id: int, item: Item, user: User):
    """
    Update an item with the given ID.

    Args:
        item_id: The ID of the item.
        item: The new information for the item.
        user: The user making the request.

    Returns:
        dict: The updated item information.
    """
    results = {"item_id": item_id, "item": item, "user": user}
    return results


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    Middleware to add a process time header to each response.

    Args:
        request: The incoming request.
        call_next: The next middleware or route in the stack.

    Returns:
        Response: The outgoing response.
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


if __name__ == "__main__":
    uvicorn.run(app)