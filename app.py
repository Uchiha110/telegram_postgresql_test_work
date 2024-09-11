import asyncio
from main import main
from database import init_db, engine
import logging
import sys
from handlers.start import send_morning_message

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

scheduler = AsyncIOScheduler()


async def setup_scheduler():
    # Установка расписания на каждый день в 7 утра
    trigger = CronTrigger(hour=7, minute=00)  # 7:00 утра каждый день
    scheduler.add_job(send_morning_message, trigger)
    scheduler.start()


async def start_app():
    await init_db(engine)  # Инициализация базы данных
    await setup_scheduler()  # Инициализация ежеднемной отправки сообщений
    await main()  # Запуск основного приложения


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(start_app())
