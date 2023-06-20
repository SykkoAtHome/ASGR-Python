from typing import Annotated
from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from pydantic.networks import EmailStr
from jose import jwt, JWTError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette import status

from database import SessionLocal
from models import Users, EventLogger, UserNotifications

router = APIRouter(prefix='/account', tags=['Authentication'])

SECRET_KEY = 'b5d79658d612f97b9083840bbf273ecea2be8e9ec38ed815f1205433d475347e'
ALGORITHM = 'HS256'
TOKEN_EXPIRE = 30


class Token(BaseModel):
    access_token: str
    token_type: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
db_dependency = Annotated[Session, Depends(get_db)]
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='account/login')


class CreateUserRequest(BaseModel):
    username: str = Field(max_length=20)
    email: EmailStr
    password: str = Field(min_length=3)

    class Config:
        schema_extra = {
            'example': {
                'username': 'username',
                'email': 'user@email.com',
                'password': 'p4ssw0rd'
            }
        }


def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')

        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized')
        return {'username': username, 'id': user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized')


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(db: db_dependency, create_user_request: CreateUserRequest):
    try:
        existing_user = db.query(Users).filter(Users.username == create_user_request.username).first()
        existing_email = db.query(Users).filter(Users.email == create_user_request.email).first()

        if existing_user:
            raise HTTPException(status_code=400, detail="Username already in use.")
        if existing_email:
            raise HTTPException(status_code=400, detail="E-mail already in use.")

        create_user_model = Users(email=create_user_request.email,
                                  username=create_user_request.username,
                                  hashed_password=bcrypt_context.hash(create_user_request.password),
                                  )
        db.add(create_user_model)
        db.flush()
        new_user_id = db.query(Users.id).filter(Users.username == create_user_request.username).first()
        event_log = EventLogger(event_type=1,
                                user_id=new_user_id[0],
                                event_body=f"New account created. Username: {create_user_request.username}, "
                                           f"user_id: {new_user_id[0]}"
                                )
        db.add(event_log)
        db.flush()
        notification_log = UserNotifications(user_id=new_user_id[0],
                                             is_visible=True,
                                             is_new=True,
                                             category=1,
                                             notification_body=f"Congratulations! Your account has been created."
                                             )
        db.add(notification_log)
        db.flush()
        return {"message": "Account created"}

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database Error")

    finally:
        db.commit()
        db.close()


@router.post("/login", response_model=Token)  # lesson 104
async def login_for_access_token(form: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: db_dependency):
    user = authenticate_user(form.username, form.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized')
    token = create_access_token(user.username, user.id, timedelta(minutes=TOKEN_EXPIRE))
    event_log = EventLogger(event_type=4,
                            user_id=user.id,
                            event_body=f"Login successful. Username: {user.username}, user_id: {user.id}"
                            )
    db.add(event_log)
    db.commit()
    return {'access_token': token, 'token_type': 'bearer'}
