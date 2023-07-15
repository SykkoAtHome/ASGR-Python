from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from starlette import status
from .auth import user_dependency, db_dependency
from models import *

router = APIRouter(prefix='/game', tags=['Game'])


# game_dependency
