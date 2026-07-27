from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.scheduler.jobs import send_due_challenges


scheduler = AsyncIOScheduler()


def start_scheduler():
    scheduler.add_job(
        send_due_challenges,
        "interval",
        minutes=1,
    )
    scheduler.start()