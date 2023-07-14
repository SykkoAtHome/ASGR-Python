from fastapi import APIRouter, HTTPException
from starlette import status
from .auth import user_dependency, db_dependency


router = APIRouter(prefix='/game', tags=['Game'])

#game_dependency