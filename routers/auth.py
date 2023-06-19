from datetime import timedelta, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status

from database import SessionLocal
from models import Users, EventLogger

router = APIRouter(prefix='/auth', tags=['Authentication'])

SECRET_KEY = '762f03016f368cb24d532e5447a05a9937b26b7924c00cb13e58f37fe7da1c3c'
ALGORITHM = 'HS256'
TOKEN_EXPIRE = 30

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str

    class Config:
        schema_extra = {
            'example': {
                'username': 'username',
                'email': 'user@email.com',
                'first_name': 'firstname',
                'last_name': 'lastname',
                'password': 'p4ssw0rd'
            }
        }


class Token(BaseModel):
    access_token: str
    token_type: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


def authenticate_user(username: str, password: str, db):  # lesson 104
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(username: str, user_id: int, user_type: int, is_active: bool, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id, 'type': user_type, 'is_active': is_active}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_type: int = payload.get('type')
        is_active: bool = payload.get('is_active')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized')
        return {'username': username, 'id': user_id, 'type': user_type, 'is_active': is_active}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized')


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency,
                      create_user_request: CreateUserRequest):
    try:
        create_user_model = Users(email=create_user_request.email,
                                  username=create_user_request.username,
                                  first_name=create_user_request.first_name,
                                  last_name=create_user_request.last_name,
                                  hashed_password=bcrypt_context.hash(create_user_request.password),
                                  user_type=3,
                                  is_active=True
                                  )
        db.add(create_user_model)
        db.flush()
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Error creating user')
    else:
        new_user_id = db.query(Users.id).filter(Users.username == create_user_request.username).first()
        event_log = EventLogger(event_type=1,
                                user_id=new_user_id[0],
                                details=f"New User:{create_user_request.first_name}, "
                                        f"username:{create_user_request.username}, "
                                        f"user_id: {new_user_id[0]}"
                                )

        db.add(event_log)
        db.commit()


@router.post("/token", response_model=Token)  # lesson 104
async def login_for_access_token(form: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: db_dependency):
    user = authenticate_user(form.username, form.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized')
    token = create_access_token(user.username, user.id, user.user_type, user.is_active, timedelta(minutes=TOKEN_EXPIRE))
    event_log = EventLogger(event_type=4,
                            user_id=user.id,
                            details=f"Login successful. Username: {user.username}, user_id: {user.id}"
                            )
    db.add(event_log)
    db.commit()
    return {'access_token': token, 'token_type': 'bearer'}
