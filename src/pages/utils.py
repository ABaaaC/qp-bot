from typing import List
from src.consts import (
    CITY_TO_TZ,
    GameType, 
    get_type_name, 
    CHOOSE_EMOJI, 
    get_city_name, 
    logger, 
    num_items_per_page, 
    LOTTERY_CITY,
    month_translations,
)

from src.schedule_loader import read_or_download_schedule, is_schedule_expired

from datetime import datetime
import pytz
from pytz import timezone

from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_filter_button_builder(filter_game_flags):
    builder = InlineKeyboardBuilder()

    for val in GameType:
        builder.add(
            InlineKeyboardButton(
                                    text = get_type_name(val) + f" {CHOOSE_EMOJI[filter_game_flags.get(val)]}",  # type: ignore
                                    callback_data=val.name
                                )
        )
    # builder.add(InlineKeyboardButton(text = "Save", callback_data='save'))
    builder.add(InlineKeyboardButton(text = "Сохранить", callback_data='save'))
    
    builder.adjust( *( [1] * (len(GameType) + 1) ) )

    return builder

async def main_menu_message(query, city):
    # await query.message.edit_text(f"Great! You chose {city}.\n"
    #                         "Now, please choose an option from the main menu:",
    #                         reply_markup=main_menu_keyboard())
    await query.message.edit_text(f"Отлично! Вы выбрали город {get_city_name(city=city)}.\n"
                        "А сейчас, выберите из меню, что душе угодно:",
                        reply_markup=main_menu_keyboard(city))
    
def main_menu_keyboard(city: str) -> InlineKeyboardMarkup:
    # keyboard = [
    #     [InlineKeyboardButton(text = "Schedule", callback_data="schedule"),
    #     InlineKeyboardButton(text = "Filter", callback_data='filter_game')]
    # ]    
    if city in LOTTERY_CITY.keys():
        keyboard = [
            [
                InlineKeyboardButton(text = "Расписание", callback_data="schedule"),
                InlineKeyboardButton(text = "Фильтры", callback_data='filter_game'),
                InlineKeyboardButton(text = "Лототрон", callback_data='lottery'),
                # InlineKeyboardButton(text = "TEST", callback_data='test'),
            ]
        ]
    else:
        keyboard = [
            [
                InlineKeyboardButton(text = "Расписание", callback_data="schedule"),
                InlineKeyboardButton(text = "Фильтры", callback_data='filter_game'),
            ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

async def filter_apply(state: FSMContext) -> None:
    state_data = await state.get_data()
    schedule = state_data.get('schedule')
    filter_game_flags = state_data.get('filter_game_flags')
    
    filtered_schedule = list(filter(lambda game: filter_game_flags.get(game.get('type')), schedule))
    await state.update_data({'filtered_schedule': filtered_schedule})

async def load_schedule(state: FSMContext):
    expiration_hours = 24
    state_data = await state.get_data()
    url = state_data.get('url') 
    logger.info(f"url:{url}")
    now = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    if 'schedule' not in state_data.keys() or state_data['schedule'] is None \
            or is_schedule_expired(state_data.get('schedule_timestamp'), state_data.get('city')): # type: ignore
        schedule, timestamp = read_or_download_schedule(state_data.get('url') + "/schedule", expiration_hours=expiration_hours) # type: ignore
        logger.info(schedule[0])
        logger.info("Done!")

        await state.update_data({'schedule': schedule, 'schedule_timestamp': timestamp})
    
        await filter_apply(state)
    # if 'filtered_schedule' not in state_data.keys() or state_data['filtered_schedule'] is None:
    #     await state.update_data({'filtered_schedule': schedule})
    #     return schedule # type: ignore
    # return state_data['filtered_schedule']

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
                   
    schedule_text = "\n\n".join(game_titles)
    return schedule_text

async def update_schedule_message(message: Message, state: FSMContext, current_page: int, num_pages: int) -> None:
    logger.info("update_schedule_message STARTED")

    state_data = await state.get_data()
    city = state_data.get('city')
    schedule = state_data.get('filtered_schedule')
    # num_items_per_page = state_data.get('num_items_per_page')
    url = state_data.get('url')

    start_index = (current_page - 1) * num_items_per_page
    end_index = min(start_index + num_items_per_page, len(schedule)) # type: ignore

    schedule_text = get_schedule_text(schedule, start_index, end_index)
    builder = InlineKeyboardBuilder()

    builder.add(
        *[
            InlineKeyboardButton(text=f"{i+1+start_index}", url=url+item.get('url_suf')) \
                for i, item in enumerate(schedule[start_index:end_index]) # type: ignore
        ]
    )

    text_callback = f"prev_{current_page - 1}_{num_pages}"
    if start_index == 0:
        text_callback = 'pass'
    builder.add(InlineKeyboardButton(text = "⬅️", callback_data=text_callback))

    text_callback = f"next_{current_page + 1}_{num_pages}"
    if start_index == len(schedule): # type: ignore
        text_callback = 'pass'
    builder.add(InlineKeyboardButton(text = "➡️", callback_data=text_callback))

    builder.add(InlineKeyboardButton(text = "🔙 Назад", callback_data="back_to_menu"))

    # message_text = f"Here is the schedule for your chosen city (Page {current_page}/{num_pages}):\n{schedule_text}"
    message_text = f"КвизПлиз{get_city_name(city).capitalize()} предлагает следующие игры, [{current_page}/{num_pages}]: \n\n{schedule_text}"
    
    builder.adjust(end_index-start_index, 2, 1)
    
    await message.edit_text(message_text, reply_markup=builder.as_markup())

    logger.info("update_schedule_message DONE")

def filter_today_games(schedule: List[dict], city: str) -> List[dict]:
    tz = timezone(CITY_TO_TZ[city])  # строка → объект часового пояса для astimezone()
    today_games = []
    for game in schedule:
        if  game.get('type') == GameType.online:
            continue

        date_str = game['date']
        time_str = game['time']

        day_str, month_str = date_str.split(',')[0].split()
        month_str = month_translations[month_str.lower()]

        dn = datetime.utcnow()
        utc_dn = pytz.utc.localize(dn)
        year_str = utc_dn.astimezone(tz).year
        current_day = utc_dn.astimezone(tz).day
        current_month = utc_dn.astimezone(tz).month

        logger.info(f"day:{day_str} \nmonth:{month_str} \nyear:{year_str} \ntime:{time_str}")
        date_dt = datetime.strptime(f"{day_str} {month_str} {year_str} {time_str}", "%d %B %Y %H:%M")
        if (date_dt.day == current_day and date_dt.month == current_month):
            game.update(datetime=date_dt.strftime("%d.%m %H:%M"))
            today_games.append(game)

    return today_games