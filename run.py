import asyncio
from os import getenv

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from src.handlers import rt
from src.database import init_db
from src.reminder_worker import check_reminders

load_dotenv()

TOKEN = getenv("TG_TOKEN")


async def on_startup():
    asyncio.create_task(check_reminders(bot=Bot(TOKEN)))


async def main() -> None:
    dp = Dispatcher()
    dp.include_router(rt)
    init_db()
    dp.startup.register(on_startup)
    bot = Bot(token=TOKEN)
    await bot.delete_webhook(True)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
