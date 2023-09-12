from typing import Any, Dict
import logging

from src.schedule_loader import GameType

from aiogram.fsm.state import State, StatesGroup



class ConversationStates(StatesGroup):
    CITY_CHOICE = State()
    MAIN_MENU = State()
    PAGES = State()
    FILTER = State()
    LOTTERY_MENU = State()
    LOTTERY = State()
    LOTTERY_GAMES = State()
    LOTTERY_TEAMS = State()
    LOTTERY_FINISH = State()

LOTTERY_FIELDS = {
    'team_name': 'LotteryPlayer[team_name]',
    'name': 'LotteryPlayer[name]',
    'email': 'LotteryPlayer[email]',
    'phone': 'LotteryPlayer[phone]',
    'date_of_birth_day': 'LotteryPlayer[date_of_birth_day]',
    'date_of_birth_month': 'LotteryPlayer[date_of_birth_month]',
    'date_of_birth_year': 'LotteryPlayer[date_of_birth_year]',
    'gender': 'LotteryPlayer[gender]'
}

LOTTERY_URL = "https://quizplease.ru/ajax/send-lottery-player-form"

# By Default we choose all filters
DEFAULT_FILTER = dict([(i, True) for i in GameType])

CITY_TO_RU_CITY = {
    'moscow': 'Москва'
}

CITY_TO_TZ = {
    'moscow': 'Europe/Moscow'
}

month_translations = {
    "января": "January",
    "февраля": "February",
    "марта": "March",
    "апреля": "April",
    "мая": "May",
    "июня": "June",
    "июля": "July",
    "августа": "August",
    "сентября": "September",
    "октября": "October",
    "ноября": "November",
    "декабря": "December"
}

LOTTERY_CITY = {
    'moscow': '2b26c3d9fc',
    'bishkek': '35830f620c'
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

def get_city_name(city: str | None = None, state_data: Dict[str, Any] | None = None) -> str:
    assert city is not None or state_data is not None
    if city is None and state_data is not None:
        city = state_data.get('city')
    return CITY_TO_RU_CITY.get(city) # type: ignore
    


CHOOSE_EMOJI = ['❌', '✅']

# Define the number of items per page
num_items_per_page = 5

# Enable logging
fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
clrd_fmt = '\x1b[38;5;226m' + fmt + '\x1b[0m'
logging.basicConfig(format=fmt, level=logging.INFO, )
logger = logging.getLogger(__name__)
