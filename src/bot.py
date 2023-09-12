from aiogram import Bot, Dispatcher, Router
from aiogram.enums import ParseMode

from dotenv import dotenv_values
config = dotenv_values(".env")
BOT_TOKEN = config.get("BOT_TOKEN")

from src.telebot10_aio import form_router
from src.pages.filters import filter_router
from src.edit_profile import form_router as profile_router

# Initialize Bot instance with a default parse mode which will be passed to all API calls
bot = Bot(BOT_TOKEN, parse_mode=ParseMode.HTML) # type: ignore

"""Start the bot."""

dp = Dispatcher()
dp.include_router(form_router)
dp.include_router(filter_router)
dp.include_router(profile_router)

