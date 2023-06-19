from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, TIMESTAMP
import datetime
from database import Base


class Users(Base):

    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    user_type = Column(Integer, ForeignKey("user_type.id"), default=3)
    create_date = Column(TIMESTAMP, default=datetime.datetime.now)
    email_confirmed = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)


class UserType(Base):

    __tablename__ = 'user_type'
    id = Column(Integer, primary_key=True, index=True)
    user_type = Column(String)


class Game(Base):

    __tablename__ = 'games'
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    directions_point = Column(String)
    game_type = Column(Integer, ForeignKey("game_type.id"))
    game_name = Column(String)
    game_description = Column(String)
    scheduled_start = Column(TIMESTAMP)
    auto_start = Column(Boolean, default=False)
    game_duration = Column(Integer)
    max_players = Column(Integer)
    teams = Column(Integer, default=0)
    created_date = Column(TIMESTAMP, default=datetime.datetime.now)
    tick_interval = Column(Integer, default=30)
    warmup = Column(Integer, default=10)
    game_current_state = Column(Integer, ForeignKey("game_state.id"))


class GameType(Base):

    __tablename__ = 'game_type'
    id = Column(Integer, primary_key=True, index=True)
    type_name = Column(String)
    type_description = Column(String)


class GameState(Base):

    __tablename__ = 'game_state'
    id = Column(Integer, primary_key=True, index=True)
    state_name = Column(String)
    state_description = Column(String)

class GameEvents(Base):

    __tablename__ = 'game_events'
    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(String, ForeignKey('games.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    event_type = Column(Integer, ForeignKey("events.id"))
    event_details = Column(String)
    event_server_time = Column(TIMESTAMP, default=datetime.datetime.now)


class EventLogger(Base):

    __tablename__ = 'event_logs'
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(Integer, ForeignKey("events.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    details = Column(String)
    timestamp = Column(TIMESTAMP, default=datetime.datetime.now)


class Events(Base):

    __tablename__ = 'events'
    id = Column(Integer, primary_key=True, index=True)
    event_name = Column(String)
    category = Column(String)
