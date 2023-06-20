from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette import status

from database import SessionLocal
from models import Users, EventLogger, UserNotifications

router = APIRouter(prefix='/account', tags=['Authentication'])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

db_dependency = Annotated[Session, Depends(get_db)]


class CreateUserRequest(BaseModel):
    username: str = Field(max_length=20)
    email: str
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
