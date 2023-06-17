from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from database import SessionLocal
from .auth import get_current_user
from models import Users

router = APIRouter(
    prefix='/su',
    tags=['SuperUser']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all_users(user: user_dependency, db: db_dependency):
    print(user)
    if user is None or user.get('type') != 1:
        raise HTTPException(status_code=403, detail='Forbidden')
    return db.query(Users).all()

