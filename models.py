import datetime

from sqlalchemy import Column, String, TIMESTAMP, Boolean
from sqlalchemy import Integer, ForeignKey

from database import Base


#  Users
class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_valid = Column(Boolean, default=False)
    user_type = Column(Integer, ForeignKey("user_type.id"), default=1)
    create_date = Column(TIMESTAMP, default=datetime.datetime.now)


class Usertype(Base):
    __tablename__ = "user_type"
    id = Column(Integer, primary_key=True, index=True)
    user_type_name = Column(String)


class UsersDetails(Base):
    __tablename__ = "users_details"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    display_name = Column(String)
    first_name = Column(String)
    last_name = Column(String)


class EmailConfirm(Base):
    __tablename__ = "email_confirmation"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    unique = Column(String, unique=True)
    is_used = Column(Boolean, default=False)
    create_date = Column(TIMESTAMP)
    expire_date = Column(TIMESTAMP)


class UserNotifications(Base):
    __tablename__ = 'user_notifications'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    is_visible = Column(Boolean, default=True)
    is_new = Column(Boolean, default=True)
    category = Column(Integer, ForeignKey("categories.id"))
    notification_body = Column(String)
    notification_date = Column(TIMESTAMP)


class EventLogger(Base):
    __tablename__ = 'event_logs'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    event_type = Column(Integer, ForeignKey("events.id"))
    event_body = Column(String)
    event_date = Column(TIMESTAMP, default=datetime.datetime.now)
    client_host = Column(String)


class Events(Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True, index=True)
    event_name = Column(String)
    category = Column(Integer, ForeignKey("categories.id"))


class Categories(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String)


#  Game


class GameStatus(Base):
    __tablename__ = 'game_status'
    id = Column(Integer, primary_key=True, index=True)
    status_name = Column(String)


class Games(Base):
    __tablename__ = 'games'
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    game_name = Column(String)
    game_lobby_lat = Column(String)
    game_lobby_lon = Column(String)
    start_date = Column(TIMESTAMP)
    auto_start = Column(Boolean, default=False)
    warmup_duration = Column(Integer)
    game_duration = Column(Integer)
    offmap_timer = Column(Integer)
    players = Column(Integer)
    teams = Column(Integer)
    created = Column(TIMESTAMP, default=datetime.datetime.now)
    game_status_id = Column(Integer, ForeignKey("game_status.id"))


class SlotType(Base):
    __tablename__ = 'slot_type'
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, unique=True)


class Roles(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String, unique=True)
    icon = Column(String)
    role_description = Column(String)


class Teams(Base):
    __tablename__ = 'teams'
    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"))
    team_name = Column(String)
    team_color = Column(String)
    team_slots = Column(Integer)


class TeamSlots(Base):
    __tablename__ = 'team_slots'
    id = Column(Integer, primary_key=True, index=True)
    slot_type = Column(Integer, ForeignKey("slot_type.id"))
    role = Column(Integer, ForeignKey("roles.id"))
    team_id = Column(Integer, ForeignKey("teams.id"))
    user_id = Column(Integer, ForeignKey("users.id"))


class ObjectTypes(Base):
    __tablename__ = 'object_types'
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, unique=True)


class MapObjects(Base):
    __tablename__ = 'map_objects'
    id = Column(Integer, primary_key=True, index=True)
    object_name = Column(String)
    object_type = Column(String, ForeignKey("object_types.type"))


class Icons(Base):
    __tablename__ = 'icons'
    id = Column(Integer, primary_key=True, index=True)
    icon_name = Column(String)
    icon_data = Column(String)
    object_type = Column(String, ForeignKey("object_types.type"))


class ShapeTypes(Base):
    __tablename__ = 'shape_types'
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, unique=True)


class MapLayer0(Base):
    __tablename__ = 'map_layer_0'
    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"))
    zone_id = Column(Integer)
    zone_name = Column(String)
    shape_type = Column(Integer, ForeignKey("shape_types.id"))
    zone_shape = Column(String)
    expires = Column(Integer)
    color = Column(String)
    kill_timer = Column(Integer)


class MapLayer1(Base):
    __tablename__ = 'map_layer_1'
    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"))
    zone_id = Column(Integer)
    zone_name = Column(String)
    shape_type = Column(Integer, ForeignKey("shape_types.id"))
    zone_shape = Column(String)
    color = Column(String)
    danger = Column(Boolean, default=False)
    kill_timer = Column(Integer)


class MapLayer2(Base):
    __tablename__ = 'map_layer_2'
    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"))
    zone_id = Column(Integer)
    zone_name = Column(String)
    shape_type = Column(Integer, ForeignKey("shape_types.id"))
    zone_shape = Column(String)
    color = Column(String)
    time_delay = Column(Integer, default=5)
    release_players = Column(Integer, default=1)


class MapLayer3(Base):
    __tablename__ = 'map_layer_3'
    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"))
    zone_id = Column(Integer)
    zone_name = Column(String)
    shape_type = Column(Integer, ForeignKey("shape_types.id"))
    zone_shape = Column(String)
    color = Column(String)
    map_object_type = Column(String, ForeignKey("object_types.type"))
    object_icon = Column(Integer, ForeignKey("icons.id"))


class MapUsers(Base):
    __tablename__ = 'map_users'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    game_id = Column(Integer, ForeignKey("games.id"))
    latitude = Column(String)
    longitude = Column(String)
    last_update = Column(TIMESTAMP)
    layer_0_zone = Column(Integer, ForeignKey("map_layer_0.id"))
    layer_1_zone = Column(Integer, ForeignKey("map_layer_1.id"))
    layer_2_zone = Column(Integer, ForeignKey("map_layer_2.id"))
    layer_3_zone = Column(Integer, ForeignKey("map_layer_3.id"))


class InGameLocationEvents(Base):
    __tablename__ = 'ingame_location_events'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    game_id = Column(Integer, ForeignKey("games.id"))
    latitude = Column(String)
    longitude = Column(String)
    timestamp = Column(TIMESTAMP)
    tick_id = Column(Integer)
