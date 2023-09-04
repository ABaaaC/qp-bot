
from src.schedule_loader import read_or_download_schedule

from dotenv import dotenv_values
config = dotenv_values(".env")
BOT_TOKEN = config.get("BOT_TOKEN")
BASE_WEBHOOK_URL = config.get("BASE_WEBHOOK_URL")
WEBHOOK_PATH = config.get("WEBHOOK_PATH")

# bind localhost only to prevent any external access
WEB_SERVER_HOST = config.get("WEB_SERVER_HOST")
# Port for incoming request from reverse proxy. Should be any available port
WEB_SERVER_PORT = config.get("WEB_SERVER_PORT")
#!/usr/bin/env python

import math
import logging
from typing import Any, Dict

from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder

from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

# Define the number of items per page
num_items_per_page = 5


form_router = Router()

# Enable logging
fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
clrd_fmt = '\x1b[38;5;226m' + fmt + '\x1b[0m'
logging.basicConfig(format=fmt, level=logging.INFO, )
logger = logging.getLogger(__name__)


# Conversation states
class ConversationStates(StatesGroup):
    CITY_CHOICE = State()
    MAIN_MENU = State()
    PAGES = State()
CITY_CHOICE, MAIN_MENU, PAGES = ConversationStates.CITY_CHOICE, ConversationStates.MAIN_MENU, ConversationStates.PAGES

# @dp.message(commands=['start'])
# to add another router
@form_router.message(CommandStart())
async def start(message: Message, state: FSMContext) -> None:
    await state.set_state(ConversationStates.CITY_CHOICE)

    logger.info("Start is really calling")
    custom_keyboard = [[InlineKeyboardButton(text="Moscow", callback_data="moscow")]]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=custom_keyboard)
    await message.answer(text="Please choose a city:", reply_markup=reply_markup)


@form_router.callback_query(ConversationStates.CITY_CHOICE)
async def city_choice(query: types.CallbackQuery, state: FSMContext) -> None:
    logger.info("city_choice STARTED")
    await state.set_data({'city': query.data})
    city = query.data

    await query.message.answer(f"Great! You chose {city}.\n"
                              "Now, please choose an option from the main menu:",
                              reply_markup=main_menu_keyboard())
    
    await state.set_state(ConversationStates.MAIN_MENU)
    logger.info("city_choice DONE")

def main_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text = "Schedule", callback_data="schedule"),
        InlineKeyboardButton(text ="Something", callback_data="something")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

@form_router.callback_query(ConversationStates.MAIN_MENU)
async def main_menu(query: types.CallbackQuery, state: FSMContext) -> None:
    logger.info("main_menu STARTED")

    if query.data == "schedule":
        await state.set_state(ConversationStates.PAGES)
        logger.info("Reading or Downloading Schedule")
        schedule = read_or_download_schedule("https://moscow.quizplease.ru/schedule", expiration_hours=24)
        logger.info(schedule[0])
        logger.info("Done!")
        
        await state.update_data({'schedule': schedule, 'page' : 0})
        current_page = 1  # Replace context.user_data with query.from_user
        num_pages = math.ceil(len(schedule) / num_items_per_page)
        await state.update_data({'num_items_per_page': num_items_per_page})
        await update_schedule_message(query.message, state, current_page, num_pages)  # Pass query.from_user to update_schedule_message

    elif query.data == "something":
        logger.info("something")
        await query.message.answer("You chose 'Something'.")  


    elif query.data == "back_to_menu":
        city = await state.get_data('city')
        await query.message.edit_text(f"Great! You chose {city}.\n"  # Replace context.user_data with query.from_user
                                      "Now, please choose an option from the main menu:",
                                      reply_markup=main_menu_keyboard())

    logger.info("main_menu DONE")


async def update_schedule_message(message: Message, state: FSMContext, current_page: int, num_pages: int) -> None:
    logger.info("update_schedule_message STARTED")

    state_data = await state.get_data()
    schedule = state_data['schedule']
    num_items_per_page = state_data['num_items_per_page']

    start_index = (current_page - 1) * num_items_per_page
    end_index = min(start_index + num_items_per_page, len(schedule))

    schedule_text = "\n".join([f"{i + 1 + start_index}. {item['title']} - {item['date']} at {item['time']} in {item['place']}" for i, item in enumerate(schedule[start_index:end_index])])
    builder = InlineKeyboardBuilder()

    if start_index > 0:
        builder.add(InlineKeyboardButton(text = "⬅️ Previous", callback_data=f"prev_{current_page - 1}_{num_pages}"))

    builder.add(InlineKeyboardButton(text = "🔙 Back", callback_data="back_to_menu"))

    if end_index < len(schedule):
        builder.add(InlineKeyboardButton(text = "➡️ Next", callback_data=f"next_{current_page + 1}_{num_pages}"))

    message_text = f"Here is the schedule for your chosen city (Page {current_page}/{num_pages}):\n{schedule_text}"
    await message.edit_text(message_text, reply_markup=builder.as_markup())

    logger.info("update_schedule_message DONE")


@form_router.callback_query(ConversationStates.PAGES)
async def button_callback(query: types.CallbackQuery, state: FSMContext):
    logger.info("button_callback STARTED")

    state_data = await state.get_data()
    num_items_per_page =  state_data.get('num_items_per_page')  # Replace context.user_data with query.from_user

    if query.data.startswith("prev_") or query.data.startswith("next_"):
        action, new_page, num_pages = query.data.split("_")
        new_page = int(new_page)
        num_pages = int(num_pages)

        if 0 <= new_page <= num_pages:

            await state.update_data({'page': new_page})
            current_page = new_page
            await update_schedule_message(query.message, state, current_page, num_pages)  # Pass query.from_user to update_schedule_message

    elif query.data == "schedule":
        current_page = 1  # Assuming you want to reset to the first page
        num_pages = math.ceil(len(state_data.get('schedule')) / num_items_per_page)  # Replace context.user_data with query.from_user
        await update_schedule_message(query.message, state, current_page, num_pages)  # Pass query.from_user to update_schedule_message

    elif query.data == "something":
        await query.message.answer("You chose 'Something'.")  # Replace query.edit_message_text with query.message.edit_text
    
    elif query.data == "back_to_menu":
        await state.set_state(ConversationStates.MAIN_MENU)
        city = state_data.get('city')
        await query.message.edit_text(f"Great! You chose {city}.\n"  # Replace context.user_data with query.from_user
                                      "Now, please choose an option from the main menu:",
                                      reply_markup=main_menu_keyboard())
    
    logger.info("button_callback DONE")

"""Start the bot."""
dp = Dispatcher()
dp.include_router(form_router)


# Initialize Bot instance with a default parse mode which will be passed to all API calls
bot = Bot(BOT_TOKEN, parse_mode=ParseMode.HTML)

