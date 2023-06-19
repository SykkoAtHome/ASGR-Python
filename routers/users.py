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
    is_active: int

    class Config:
        schema_extra = {
            'example': {
                'new_firstname': 'NewFirstName',
                'new_lastname': 'NewLastName',
                'is_active': 'true'
            }
        }


@router.get("/", status_code=status.HTTP_200_OK)
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
        raise HTTPException(status_code=401, detail='Unauthorized')
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
    user_model.first_name = edit_user.new_firstname
    user_model.last_name = edit_user.new_lastname
    user_model.is_active = edit_user.is_active
    event_log = EventLogger(event_type=7,
                            user_id=user.get('id'),
                            details=f"New first name: {edit_user.new_firstname}, new last name: {edit_user.new_lastname}"
                            )
    db.add(event_log)
    db.commit()

