import asyncio
import logging.config
import os

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats

from src.tg_bot.middlewares.db import DataBaseSession
from src.database.engine import session_maker
from src.tg_bot.handlers.user_private import user_private_router
from src.settings.logging_settings import LOGGING


logging.config.dictConfig(LOGGING)

commands = [BotCommand(command='start', description='Сделать заказ'),]

ALLOWED_UPDATES = ['message', 'callback_query']

bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))
dp = Dispatcher()
dp.include_router(user_private_router)


async def main():
    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.delete_my_commands(scope=BotCommandScopeAllPrivateChats())
    await bot.set_my_commands(commands=commands, scope=BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot, allowed_updates=ALLOWED_UPDATES)

asyncio.run(main())
