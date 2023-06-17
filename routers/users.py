from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status

from database import SessionLocal
from models import Users
from .auth import get_current_user

router = APIRouter(prefix='/user', tags=['Users'])


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
    new_password: str

    class Config:
        schema_extra = {
            'example': {
                'password': 'old_password',
                'new_password': 'new_password'
            }
        }

class UpdateUser(BaseModel):
    new_firstname: str
    new_lastname: str

    class Config:
        schema_extra = {
            'example': {
                'new_firstname': 'NewFirstName',
                'new_lastname': 'NewLastName'
            }
        }


@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication failed')
    return db.query(Users).filter(Users.id == user.get('id')).first()


@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency, user_verification: UpdateUserPassword):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication failed')
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()

    if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
        raise HTTPException(status_code=401, detail='Error on password change')
    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)
    db.add(user_model)
    db.commit()

@router.put("/update", status_code=status.HTTP_204_NO_CONTENT)
async def update_user(user: user_dependency, db: db_dependency, update_user: UpdateUser):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication failed')
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    user_model.first_name = update_user.new_firstname
    user_model.last_name = update_user.new_lastname
    db.commit()
