from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from cfg.cfg import bot
from handlers.start import start_commands, send_morning_message
from handlers.start import router as start_router

storage = MemoryStorage()


async def main() -> None:
    dp = Dispatcher(storage=storage)

    dp.include_router(start_router)

    await start_commands(dp)

    await dp.start_polling(bot, skip_updates=True)
