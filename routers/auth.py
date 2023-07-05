from typing import Annotated
from datetime import timedelta

import requests
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from pydantic.networks import EmailStr
from jose import jwt, JWTError
from requests.exceptions import SSLError, JSONDecodeError
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette import status
from datetime import datetime
import random
import string

from urllib3.exceptions import MaxRetryError

from database import SessionLocal
from models import Users, EventLogger, UserNotifications, EmailConfirm
from sendmail import send_email_verification

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
    email: EmailStr
    password: str = Field(min_length=3)

    class Config:
        schema_extra = {
            'example': {
                'email': 'user@email.com',
                'password': 'p4ssw0rd'
            }
        }


class UpdateUserPassword(BaseModel):
    password: str
    new_password: str = Field(min_length=6)

    class Config:
        schema_extra = {
            'example': {
                'password': 'current_password',
                'new_password': 'new_password'
            }
        }


def authenticate_user(email: str, password: str, db):
    user = db.query(Users).filter(Users.email == email).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        event_log = EventLogger(event_type=5,
                                user_id=user.id,
                                event_body=f"Login failed. Account: {user.email}, user_id: {user.id}. Wrong password.")
        db.add(event_log)
        db.commit()
        return False
    return user


def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id}
    expires = datetime.now() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get('sub')
        user_id: int = payload.get('id')
        if email is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized')
        return {'email': email, 'id': user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized')


user_dependency = Annotated[dict, Depends(get_current_user)]


def check_user_logs(db, user_id, event_type, time_delta):
    start_time = datetime.now() - timedelta(minutes=time_delta)
    query = db.query(func.count()). \
        filter(EventLogger.user_id == user_id). \
        filter(EventLogger.event_type == event_type). \
        filter(EventLogger.event_date >= start_time).scalar()
    return query


def email_activation(db: db_dependency, user_id, date_time):
    unique = ''.join(random.choices(string.ascii_letters + string.digits, k=24))
    query = EmailConfirm(user_id=user_id,
                         unique=unique,
                         create_date=date_time,
                         expire_date=date_time + timedelta(hours=24))

    db.add(query)
    db.commit()

# def send_email():


def get_user_ip():
    response = requests.get('https://api.ipify.org?format=json').json()
    return response["ip"]


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(db: db_dependency, create_user_request: CreateUserRequest):
    try:
        existing_email = db.query(Users).filter(Users.email == create_user_request.email).first()

        if existing_email:
            raise HTTPException(status_code=400, detail="E-mail already in use.")

        date_time = datetime.now()
        create_user_model = Users(email=create_user_request.email,
                                  hashed_password=bcrypt_context.hash(create_user_request.password),
                                  create_date=date_time
                                  )
        db.add(create_user_model)
        db.flush()
        new_user_id = create_user_model.id
        email_activation(db, create_user_model.id, date_time)
        event_log = EventLogger(event_type=1,
                                user_id=new_user_id,
                                event_body=f"New account created. Account: {create_user_request.email}, "
                                           f"user_id: {new_user_id}",
                                event_date=date_time,
                                client_host=get_user_ip()
                                )
        db.add(event_log)

        notification_log = UserNotifications(user_id=new_user_id,
                                             is_visible=True,
                                             is_new=True,
                                             category=1,
                                             notification_body=f"Congratulations! Your account has been created.",
                                             notification_date=date_time
                                             )
        db.add(notification_log)
        db.flush()
        send_email_verification(new_user_id, db)

        return {"message": "Account created"}

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database Error")
    except JSONDecodeError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error processing data")
    except (SSLError, MaxRetryError):
        db.rollback()
        raise HTTPException(status_code=500, detail="ipify.org offline")
    finally:
        db.commit()
        db.close()


@router.post("/login", response_model=Token)
async def login_for_access_token(form: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(form.username, form.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized')
    account_status = db.query(Users.is_active).filter(Users.email == form.username).scalar()
    if account_status == 0:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Account disabled')
    token = create_access_token(user.email, user.id, timedelta(minutes=TOKEN_EXPIRE))
    event_log = EventLogger(event_type=4,
                            user_id=user.id,
                            event_body=f"Login successful. Account: {user.email}, user_id: {user.id}",
                            client_host=get_user_ip())
    db.add(event_log)
    db.commit()
    return {'access_token': token, 'token_type': 'bearer'}


@router.get("/confirm_email/{unique}")
async def confirm_user_email(db: db_dependency, unique):
    email_unique = db.query(EmailConfirm).filter(EmailConfirm.unique == unique).order_by(EmailConfirm.id.desc()).first()
    if not email_unique or email_unique.expire_date < datetime.now():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found')
    if email_unique.is_used == 1:
        raise HTTPException(status_code=status.HTTP_410_GONE, detail='Gone')
    user = db.query(Users).filter(Users.id == email_unique.user_id).first()
    user.is_valid = True
    email_unique.is_used = True
    event_log = EventLogger(event_type=15,
                            user_id=user.id,
                            event_body=f"Email confirmed. Account: {user.email}, "
                                       f"user_id: {user.id}"
                            )
    db.add(event_log)
    db.commit()
    db.close()
    return {"message": "Email confirmed"}


@router.put("/update_password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency, user_verification: UpdateUserPassword):
    if user is None:
        raise HTTPException(status_code=401, detail='Unauthorized')
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()

    if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
        raise HTTPException(status_code=400, detail='Current password is wrong')

    if user_verification.password == user_verification.new_password:
        raise HTTPException(status_code=400, detail='New password must be different from the current password')

    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)
    event_log = EventLogger(event_type=6,
                            user_id=user.get('id'),
                            details=f"Password changed for username: {user.get('username')}"
                            )
    db.add(user_model)
    db.add(event_log)
    db.commit()
