from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler

from database import SessionLocal
from models import AppEventsLogger, AppServicesSettings

db = SessionLocal()
scheduler = BackgroundScheduler()


def main_app_log(service: str, event: str):
    try:
        app_event = AppEventsLogger(service_name=f"{service}",
                                    event_body=event,
                                    event_date=datetime.now())
        db.add(app_event)
        db.commit()
    finally:
        db.close()


def process_services():
    services = db.query(AppServicesSettings).filter(AppServicesSettings.is_active == True).all()
    if not services:
        return None
    service_dict = {service.service_name: service.service_interval for service in services}
    return service_dict

