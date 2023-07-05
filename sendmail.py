from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Annotated
from database import SessionLocal
from models import EmailConfirm, Users
import smtplib


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

login = "11d6f8dbafbd24"
password = "38c92d7a8189f9"


def send_email_verification(user_id, db: db_dependency):
    user = db.query(Users).filter(Users.id == user_id).first()
    confirm = db.query(EmailConfirm).filter(EmailConfirm.user_id == user_id).first()
    if not confirm:
        return False

    sender_email = "No Reply <no-reply@asgr-game.com>"
    receiver_email = f"{user.email}"

    message = MIMEMultipart("alternative")
    message["Subject"] = "Welcome to ASGR. Please confirm your e-mail address"
    message["From"] = sender_email
    message["To"] = receiver_email

    text = f"Hi,\n" \
           f"This message was automatically generated during the account creation process in the ASGR application.\n" \
           f"To confirm your email address, please click the link below.\n\n" \
           f"http://127.0.0.1:8000/account/confirm_email/{confirm.unique}\n\n" \
           f"Link is active for 24 hours."

    html = f"""\
    <html>
      <body>
        <p>Hi,<br>
           This message was automatically generated during the account creation process in the ASGR application.<br>
           To confirm your email address, please click the link below.</p>
        <p><a href="http://127.0.0.1:8000/account/confirm_email/{confirm.unique}">Confirm e-mail</a></p>
        <p> Link is active for 24 hours.</p>
      </body>
    </html>
    """

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    message.attach(part1)
    message.attach(part2)

    with smtplib.SMTP("sandbox.smtp.mailtrap.io", 2525) as server:
        server.login(login, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
