from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status

from database import SessionLocal
from models import Users, EventLogger
from .auth import get_current_user

router = APIRouter(prefix='/user', tags=['User'])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class UpdateUserPassword(BaseModel):
    password: str
    new_password: str = Field(min_length=6)

    class Config:
        schema_extra = {
            'example': {
                'password': 'current_password',
                'new_password': 'new_password_min_6'
            }
        }


class UpdateUser(BaseModel):
    new_firstname: str
    new_lastname: str

    class Config:
        schema_extra = {
            'example': {
                'new_firstname': 'NewFirstName',
                'new_lastname': 'NewLastName',
            }
        }


@router.get("", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Unauthorized')
    return db.query(Users).filter(Users.id == user.get('id')).first()


@router.put("/update/password", status_code=status.HTTP_204_NO_CONTENT)
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


@router.put("/update", status_code=status.HTTP_204_NO_CONTENT)
async def update_user(user: user_dependency, db: db_dependency, edit_user: UpdateUser):
    if user is None:
        raise HTTPException(status_code=401, detail='Unauthorized')
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    event_detail = {}
    if user_model.first_name != edit_user.new_firstname:
        event_detail['Old first name'] = user_model.first_name
        event_detail['New first name'] = edit_user.new_firstname
        user_model.first_name = edit_user.new_firstname

    if user_model.last_name != edit_user.new_lastname:
        event_detail['Old last name'] = user_model.last_name
        event_detail['New last name'] = edit_user.new_lastname
        user_model.last_name = edit_user.new_lastname
    if len(event_detail) > 0:
        formatted_detail = ", ".join([f"{key}: {value}" for key, value in event_detail.items()])
        event_log = EventLogger(event_type=7, user_id=user.get('id'),
                                details=formatted_detail)
        db.add(event_log)
        db.commit()
    else:
        raise HTTPException(status_code=200, detail='Nothing to do')

