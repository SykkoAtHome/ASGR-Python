from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from database import SessionLocal


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
