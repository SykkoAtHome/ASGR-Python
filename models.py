from sqlalchemy import Column, String, TIMESTAMP, Boolean
from sqlalchemy import Integer, ForeignKey
import datetime

from database import Base


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    create_date = Column(TIMESTAMP, default=datetime.datetime.now)


class UserNotifications(Base):
    __tablename__ = 'user_notifications'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    is_visible = Column(Boolean, default=True)
    is_new = Column(Boolean, default=True)
    category = Column(Integer, ForeignKey("categories.id"))
    notification_body = Column(String)
    notification_date = Column(TIMESTAMP, default=datetime.datetime.now)


class EventLogger(Base):
    __tablename__ = 'event_logs'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    event_type = Column(Integer, ForeignKey("events.id"))
    event_body = Column(String)
    event_date = Column(TIMESTAMP, default=datetime.datetime.now)


class Events(Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True, index=True)
    event_name = Column(String)
    category = Column(Integer, ForeignKey("categories.id"))


class Categories(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String)
