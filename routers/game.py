from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from database import SessionLocal
from .auth import get_current_user
from models import Game, EventLogger
import datetime

router = APIRouter(
    prefix='/game',
    tags=['game']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
game_dependency = Annotated[dict, Depends(get_current_user)]


class CreateGameRequest(BaseModel):
    game_name: str = Field(max_length=24, default='Short game name')
    game_description: str = Field(max_length=240, default='Game description')
    directions_point: str = Field(default='(52.01958,20.98463)')
    game_type: int = Field(gt=0, default=1)
    scheduled_start: str = Field(default='2023-12-24 18:00:00')
    game_duration: int = Field(gt=4, default=10, )
    max_players: int = Field(lt=32, default=8)
    teams: int = Field(lt=6)
    warmup: int = Field(gt=0, default=10)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_game(user: user_dependency, db: db_dependency,
                      create_game_request: CreateGameRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Unauthorized')
    if user.get('is_active') == 0:
        raise HTTPException(status_code=403, detail='Forbidden')
    try:
        create_game_model = Game(owner_id=user.get('id'),
                                 game_name=create_game_request.game_name,
                                 game_description=create_game_request.game_description,
                                 directions_point=create_game_request.directions_point,
                                 game_type=create_game_request.game_type,
                                 scheduled_start=create_game_request.scheduled_start,
                                 game_duration=create_game_request.game_duration,
                                 max_players=create_game_request.max_players,
                                 teams=create_game_request.teams,
                                 tick_interval=15,
                                 warmup=create_game_request.warmup,
                                 game_current_state=1
                                 )
        db.add(create_game_model)
        db.flush()
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Error creating game')
    else:
        new_game_id = db.query(Game.id).filter(Game.game_name == create_game_request.game_name).first()
        event_log = EventLogger(event_type=9,
                                user_id=user.get('id'),
                                details=f"New game: {create_game_request.game_name}. "
                                        f"Created by username: {user.get('username')}, "
                                        f"user_id: {user.get('id')}, "
                                        f"game_id: {new_game_id}"
                                )
        db.add(event_log)
        db.commit()
