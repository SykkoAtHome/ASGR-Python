from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
import models
from app_tasks import scheduled_services
from app_tasks.startup import main_app_log, process_services
from db_data.default_data import db_default_data

from database import engine
from routers import auth, game

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

scheduler = BackgroundScheduler()

app.include_router(auth.router)
app.include_router(game.router)


@app.on_event("startup")
async def startup_event():
    main_app_log("Main App", "START")
    service_dict = process_services()

    if service_dict is not None:
        for service_name, service_interval in service_dict.items():
            service_func = getattr(scheduled_services, service_name)
            scheduler.add_job(service_func, 'interval', seconds=service_interval)

        scheduler.print_jobs()
        main_app_log("Scheduler", f"START. Services: {len(service_dict)}")

    scheduler.start()
    db_default_data()


@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()
    main_app_log("Main App", "STOP")
