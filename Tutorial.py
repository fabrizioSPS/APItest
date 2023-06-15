import json
import time
from datetime import datetime, timedelta
from typing import Annotated, Union, List, Any

import uvicorn
from fastapi import FastAPI, Request, Path, Form, UploadFile, File, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

import database
from InternalCode.json_parser import parse_Json
from database import SessionLocal
from pydanticApiModels import Item, UserInDB, TokenData, User, Token, UserInfo
from . import pydanticApiModels as schemas

app = FastAPI()

"""
Authentication
"""
SECRET_KEY = "66d5528fbd7adc9cb5446d6a37e2c5fce851beeb78e0cbd3017b9f8b00434dc3"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
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
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
        current_user: Annotated[UserInfo, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token", response_model=Token)
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
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
async def read_users_me(
        current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user


@app.post("/users/", response_model=User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = database.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return database.create_user(db=db, user=user)


@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = database.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = database.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/login/")
async def login(username: Annotated[str, Form()], password: Annotated[str, Form()]):
    return {"username": username}


@app.post("/register/")
async def register(User: Annotated[Any, Depends(User)]):
    return User.username


@app.get("/")
async def StartPage():
    content = """
    <body>
    <form action="/login/" enctype="multipart/form-data" method="post">
    <input name="username" type="string">
    <input name="password" type="string">
    <input type="submit">
    </form>
    <form action="/register/" enctype="multipart/form-data" method="post">
    <input name="username" type="string">
    <input name="age" type="string">
    <input name="password" type="string">
    <input type="submit">
    </form>
    </body>
        """
    return HTMLResponse(content=content)


"""
Database
"""

"""
Reading and loading in JSON files.
"""


@app.post("/uploadfiles/", dependencies=[Depends(oauth2_scheme)])
async def create_upload_files(
        files: Annotated[
            List[UploadFile], File(description="Multiple files as UploadFile")
        ],
):
    json_file = files[0].file
    json_file.seek(0)
    json_data = json.load(json_file)
    Parsed_input = parse_Json(json_data)
    return Parsed_input


@app.get("/read_json/", dependencies=[Depends(oauth2_scheme)])
async def read_json():
    content = """
    <body>
    <form action="/uploadfiles/" enctype="multipart/form-data" method="post">
    <input name="files" type="file" multiple>
    <input type="submit">
    </form>
    </body>
        """
    return HTMLResponse(content=content)


"""
Extra tutorial steps that might become useful
"""


@app.get("/items/int/{item_id}")
async def read_int(
        item_id: Annotated[int, Path(title="The ID of the item to get", gt=0, le=1000)],
        q: str,
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results


@app.put("/items/multiplebodies/{item_id}")
async def update_item(item_id: int, item: Item, user: User):
    results = {"item_id": item_id, "item": item, "user": user}
    return results


# Middleware is a function that works with every request before it is processed by any specific path operation.
# And also with every response before returning it.
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


if __name__ == "__main__":
    uvicorn.run(app)
