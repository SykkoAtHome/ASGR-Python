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
    id = Column(Integer, primary_key=True)
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
