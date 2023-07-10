from starlette.responses import HTMLResponse
from database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends
from models import Users


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


def email_confirmed():
    with open("html/confirm_email_thankyou.html", "r") as file:
        html_content = file.read()
    return html_content
