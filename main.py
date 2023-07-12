from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
import models
from database import engine
from routers import auth, game
from app_tasks.scheduled_tasks import my_task

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(game.router)

scheduler = BackgroundScheduler()


# scheduler.add_job(my_task, 'interval', seconds=10)


@app.on_event("startup")
async def startup_event():
    scheduler.start()


@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()
