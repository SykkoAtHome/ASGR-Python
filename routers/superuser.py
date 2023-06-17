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


@router.get("/user", status_code=status.HTTP_200_OK)
async def read_all_users(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Not authenticated')
    if user.get('type') != 1:
        raise HTTPException(status_code=403, detail='Forbidden')
    return db.query(Users).all()


@router.delete("/user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user: user_dependency, db: db_dependency, user_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Not authenticated')
    if user.get('type') != 1:
        raise HTTPException(status_code=403, detail='Forbidden')
    user_model = db.query(Users).filter(Users.id == user_id).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail='User not found.')
    db.query(Users).filter(Users.id == user_id).delete()
    db.commit()
