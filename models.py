from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
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
    is_active = Column(Boolean, default=True)


class UserType(Base):
    __tablename__ = 'user_type'
    id = Column(Integer, primary_key=True, index=True)
    user_type = Column(String)

# class Game(Base):
#     __tablename__ = 'games'
#     id = Column(Integer, primary_key=True, index=True)
#     owner_id = Column(Integer, ForeignKey("users.id"))
#     directions_point = Column(String)
#     game_type = Column(Integer, ForeignKey("game_types.id"))
#     scheduled_start = Column(DateTime(timezone=True))
#     game_duration = Column(Integer)
#     max_players = Column(Integer)
#     created_date = Column(DateTime(timezone=True), server_default=func.now())
#     is_active = Column(Boolean, default=False)
#
# class GameType(Base):
#     __tablename__ = 'game_types'
#     id = Column(Integer, primary_key=True, index=True)
#     type_name = Column(String)
#     type_description = Column(String)