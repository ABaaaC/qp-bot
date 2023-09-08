
from src.schedule_loader import read_or_download_schedule, GameType, is_schedule_expired

from dotenv import dotenv_values
config = dotenv_values(".env")
BOT_TOKEN = config.get("BOT_TOKEN")
BASE_WEBHOOK_URL = config.get("BASE_WEBHOOK_URL")
WEBHOOK_PATH = config.get("WEBHOOK_PATH")
QP_URL = config.get("QP_URL")

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
    FILTER = State()


# By Default we choose all filters
DEFAULT_FILTER = dict([(i, True) for i in GameType])

CITY_TO_RU_CITY = {
    'moscow': 'Москва'
}

GAMETYPE_TO_RU = {
    GameType.online: 'Онлайн',
    GameType.newbie: "Новички",
    GameType.classic: "Классика",
    GameType.kim: "Кино и Музыка (КиМ)",
    GameType.special: "Особые",
}

def get_type_name(game_type: GameType):
    return GAMETYPE_TO_RU.get(game_type)

def get_city_name(city: str = None, state_data: Dict[str, Any] = None):
    assert city is not None or state_data is not None
    if city is None:
        city = state_data.get('city')
    return CITY_TO_RU_CITY.get(city)


CHOOSE_EMOJI = ['❌', '✅']

@form_router.message(CommandStart())
async def start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(ConversationStates.CITY_CHOICE)

    logger.info("Start is really calling")
    city = "moscow"
    custom_keyboard = [[InlineKeyboardButton(text=get_city_name(city), callback_data=city)]]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=custom_keyboard)
    # await message.answer(text="Please choose a city:", reply_markup=reply_markup)
    await message.answer(text="Пожалуйста, выберете город:", reply_markup=reply_markup)


async def main_menu_message(query, city):
    # await query.message.edit_text(f"Great! You chose {city}.\n"
    #                         "Now, please choose an option from the main menu:",
    #                         reply_markup=main_menu_keyboard())
    await query.message.edit_text(f"Отлично! Вы выбрали город {get_city_name(city=city)}.\n"
                        "А сейчас, выберите из меню, что душе угодно:",
                        reply_markup=main_menu_keyboard())

@form_router.callback_query(ConversationStates.CITY_CHOICE)
async def city_choice(query: types.CallbackQuery, state: FSMContext) -> None:
    logger.info("city_choice STARTED")
    await state.set_data({'city': query.data, 'filter_game_flags': DEFAULT_FILTER})
    city = query.data
    await state.update_data({'url': f'https://{city}.{QP_URL}'})

    await main_menu_message(query, city)
    
    await state.set_state(ConversationStates.MAIN_MENU)
    logger.info("city_choice DONE")

def main_menu_keyboard() -> InlineKeyboardMarkup:
    # keyboard = [
    #     [InlineKeyboardButton(text = "Schedule", callback_data="schedule"),
    #     InlineKeyboardButton(text = "Filter", callback_data='filter_game')]
    # ]    
    keyboard = [
        [InlineKeyboardButton(text = "Расписание", callback_data="schedule"),
        InlineKeyboardButton(text = "Фильтры", callback_data='filter_game')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

async def load_schedule(state: FSMContext):
    state_data = await state.get_data()
    if 'schedule' not in state_data.keys() or state_data['schedule'] is None \
            or is_schedule_expired(state_data.get('schedule_timestamp'), state_data.get('city')):
        schedule, timestamp = read_or_download_schedule(state_data.get('url') + "/schedule", expiration_hours=24)
        logger.info(schedule[0])
        logger.info("Done!")

        await state.update_data({'schedule': schedule, 'schedule_timestamp': timestamp})
    
    if 'filtered_schedule' not in state_data.keys() or state_data['filtered_schedule'] is None:
        await state.update_data({'filtered_schedule': schedule})
        return schedule
    return state_data['filtered_schedule']

@form_router.callback_query(ConversationStates.MAIN_MENU)
async def main_menu(query: types.CallbackQuery, state: FSMContext) -> None:
    logger.info("main_menu STARTED")

    if query.data == "schedule":
        await state.set_state(ConversationStates.PAGES)
        logger.info("Reading or Downloading Schedule")
        schedule = await load_schedule(state)
        await state.update_data({'page' : 0})
        num_pages = math.ceil(len(schedule) / num_items_per_page)
        current_page = min(1, num_pages)  # Replace context.user_data with query.from_user
        await state.update_data({'num_items_per_page': num_items_per_page})
        await update_schedule_message(query.message, state, current_page, num_pages)  # Pass query.from_user to update_schedule_message

    elif query.data == "back_to_menu":
        state_data = await state.get_data()
        city = state_data.get('city')

        await main_menu_message(query, city)

    elif query.data == 'filter_game':
        await state.set_state(ConversationStates.FILTER)
        logger.info("Edit Filters")
        schedule = await load_schedule(state)
        await filter_game(query.message, state)

    logger.info("main_menu DONE")

def get_filter_button_builder(filter_game_flags):
    builder = InlineKeyboardBuilder()

    for val in GameType:
        builder.add(
            InlineKeyboardButton(text = get_type_name(val) + f" {CHOOSE_EMOJI[filter_game_flags.get(val)]}", \
                        callback_data=val.name)
        )
    # builder.add(InlineKeyboardButton(text = "Save", callback_data='save'))
    builder.add(InlineKeyboardButton(text = "Сохранить", callback_data='save'))
    
    builder.adjust( *( [1] * (len(GameType) + 1) ) )

    return builder

async def filter_game(message: Message, state: FSMContext):
    state_data = await state.get_data()
    filter_game_flags = state_data.get('filter_game_flags')
    builder = get_filter_button_builder(filter_game_flags)
    # await message.edit_text(text = 'Choose interesting games:', reply_markup=builder.as_markup())
    await message.edit_text(text = 'Какие игры оставить?', reply_markup=builder.as_markup())

@form_router.callback_query(ConversationStates.FILTER)
async def process_filters(query: types.CallbackQuery, state: FSMContext):
    logger.info("city_choice STARTED")
    state_data = await state.get_data()

    if query.data == 'save':
        city = state_data.get('city')
        schedule = state_data.get('schedule')
        filter_game_flags = state_data.get('filter_game_flags')

        
        filered_schedule = list(filter(lambda game: filter_game_flags.get(game.get('type')), schedule))
        await state.update_data({'filtered_schedule': filered_schedule})

        await main_menu_message(query, city)
    
        await state.set_state(ConversationStates.MAIN_MENU)

    elif query.data in GameType.__members__:
        name = query.data
        game_type = getattr(GameType, name)
        filter_game_flags = state_data.get('filter_game_flags')
        filter_game_flags[game_type] = not filter_game_flags[game_type]
        await state.update_data({'filter_game_flags' : filter_game_flags})
        builder = get_filter_button_builder(filter_game_flags)
        await query.message.edit_reply_markup(reply_markup=builder.as_markup())

def get_schedule_text(schedule, start_index, end_index):
    game_titles = []
    for i, game in enumerate(schedule[start_index:end_index]):
        package_number_str = ''
        if game['package_number'] is not None:
            package_number_str = f" #{game['package_number']}"
        game_name = f"{i + 1 + start_index}. {game['title']}" + package_number_str

        if game['type'] == GameType.online:
            game_loc = f"{game['date']}, {game['time']}, ({game['price']})"
        else:
            game_loc = f"{game['date']} в {game['time']} в {game['place']} ({game['price']})"

        game_titles.append(game_name + ' - ' + game_loc)
                   
    schedule_text = "\n".join(game_titles)
    return schedule_text

async def update_schedule_message(message: Message, state: FSMContext, current_page: int, num_pages: int) -> None:
    logger.info("update_schedule_message STARTED")

    state_data = await state.get_data()
    city = state_data.get('city')
    schedule = state_data.get('filtered_schedule')
    num_items_per_page = state_data.get('num_items_per_page')
    url = state_data.get('url')

    start_index = (current_page - 1) * num_items_per_page
    end_index = min(start_index + num_items_per_page, len(schedule))

    schedule_text = get_schedule_text(schedule, start_index, end_index)
    builder = InlineKeyboardBuilder()

    builder.add(
        *[
            InlineKeyboardButton(text=f"{i+1+start_index}", url=url+item.get('url_suf')) \
                for i, item in enumerate(schedule[start_index:end_index])
        ]
    )

    text_callback = f"prev_{current_page - 1}_{num_pages}"
    if start_index == 0:
        text_callback = 'pass'
    builder.add(InlineKeyboardButton(text = "⬅️", callback_data=text_callback))

    text_callback = f"next_{current_page + 1}_{num_pages}"
    if start_index == len(schedule):
        text_callback = 'pass'
    builder.add(InlineKeyboardButton(text = "➡️", callback_data=text_callback))

    builder.add(InlineKeyboardButton(text = "🔙 Назад", callback_data="back_to_menu"))

    # message_text = f"Here is the schedule for your chosen city (Page {current_page}/{num_pages}):\n{schedule_text}"
    message_text = f"КвизПлиз{get_city_name(city).capitalize()} предлагает следующие игры, [{current_page}/{num_pages}]: \n{schedule_text}"
    
    builder.adjust(end_index-start_index, 2, 1)
    
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
        await query.message.answer("You chose 'Something'.") 
        # await query.message.edit_text(text="")
        # # Replace query.edit_message_text with query.message.edit_text
    
    elif query.data == "back_to_menu":
        await state.set_state(ConversationStates.MAIN_MENU)
        city = state_data.get('city')
        await main_menu_message(query, city)
    
    logger.info("button_callback DONE")

"""Start the bot."""
dp = Dispatcher()
dp.include_router(form_router)


# Initialize Bot instance with a default parse mode which will be passed to all API calls
bot = Bot(BOT_TOKEN, parse_mode=ParseMode.HTML)

