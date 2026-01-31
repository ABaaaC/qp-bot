
from src.consts import (
    ConversationStates,
    ProfileState,
    DEFAULT_FILTER,
    get_city_name,
    num_items_per_page,
    logger,
    CITY_TO_TZ,
    LOTTERY_FIELDS,
    LOTTERY_URL,
    loto_profiles
)

from src.pages.utils import (
    main_menu_message,
    main_menu_keyboard,
    load_schedule,
    update_schedule_message,
    filter_today_games,
) 
from src.pages.filters import filter_game

from src.edit_profile import (
    enter_test as start_profile_editing, 
    # loto_profiles, 
    lottery_request, 
    lottery_menu, 
    show_profile
)

import os, json
from datetime import datetime

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

from aiogram.enums import ParseMode
from aiogram import types, Router #,F
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder

from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.types.input_file import FSInputFile

from aiohttp import ClientSession, FormData

form_router = Router()

# List to store user IDs
user_ids = set()



@form_router.message(CommandStart())
async def start(message: Message, state: FSMContext) -> None:
    # global loto_profiles
    user_id = str(message.from_user.id)
    user_ids.add(user_id)  # type: ignore
    # logger.info(f"ID:\t{user_id}")
    # logger.info(f"loto_profiles:\t{loto_profiles}")

    await state.clear()
    # профиль грузим по городу в city_choice, здесь город ещё не выбран
    await state.set_state(ConversationStates.CITY_CHOICE)
    
    should_update = False
    # Should we update file_id ?
    # should_update = True
    # try:
    #     with open("file_id_metadata.json", "r") as f:
    #         metadata = json.load(f)
    #         last_update = datetime.fromisoformat(metadata["last_update"])
    #         should_update = (datetime.now() - last_update).days >= 190
    # except:
    #     pass

    if should_update:
        # generate file_id's
        file_id_dict = {}
        for i in range(1, 400):
            screenshot_path = os.getcwd() + '/' + f"screenshots/lottery_number_{i}.png"
            photo = FSInputFile(path=screenshot_path)
            sent_message = await message.answer_photo(photo=photo)
            file_id = sent_message.photo[-1].file_id
            file_id_dict[i] = file_id
            await sent_message.delete()
            if i % 40 == 0:
                logger.info(f"Generated {i} file_ids")
        with open("file_id_dict.json", "w") as outfile:
        # with open("file_id_dict_test.json", "w") as outfile:
            json.dump(file_id_dict, outfile, indent=4)

        with open("file_id_metadata.json", "w") as outfile:
            json.dump({"last_update": datetime.now().isoformat()}, outfile)

    logger.info("Start is really calling")
    custom_keyboard = [
        [InlineKeyboardButton(text=get_city_name("moscow"), callback_data="moscow")],
        [InlineKeyboardButton(text=get_city_name("almaty"), callback_data="almaty")],
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=custom_keyboard)
    # await message.answer(text="Please choose a city:", reply_markup=reply_markup)
    await message.answer(text="Пожалуйста, выберете город:", reply_markup=reply_markup)


@form_router.callback_query(ConversationStates.CITY_CHOICE)
async def city_choice(query: types.CallbackQuery, state: FSMContext) -> None:
    logger.info("city_choice STARTED")
    # user_id = query.message.from_user.id
    # await state.set_data({'city': query.data, 'filter_game_flags': DEFAULT_FILTER})
    await state.update_data(city = query.data)
    await state.update_data(filter_game_flags = DEFAULT_FILTER.copy())
    await state.update_data(actual_message = query.message)

    state_data = await state.get_data()
    # logger.info(f"User_ID: {user_id}\n{state_data}")

    # await state.update_data(user_id = {'city': query.data, 
    #                             'filter_game_flags': DEFAULT_FILTER,
    #                             'actual_message': query.message})
    city = query.data
    await state.update_data({'url': f'https://{city}.{QP_URL}'})
    # профиль у каждого пользователя свой на каждый город
    user_id = str(query.from_user.id)
    profile_key = f"{user_id}:{city}"
    profile_data = loto_profiles.get(profile_key)
    if profile_data:
        await state.update_data(profile_data=profile_data.copy())
    else:
        await state.update_data(profile_data=None)
    logger.info("Reading or Downloading Schedule")

    await main_menu_message(query, city)
    await load_schedule(state)
    
    await state.set_state(ConversationStates.MAIN_MENU)
    logger.info("city_choice DONE")



@form_router.callback_query(ConversationStates.MAIN_MENU)
async def main_menu(query: types.CallbackQuery, state: FSMContext) -> None:
    logger.info("main_menu STARTED")

    if query.data == "schedule":
        await state.set_state(ConversationStates.PAGES)
        await state.update_data({'page' : 0})
        await load_schedule(state)
        state_data = await state.get_data()
        schedule = state_data.get('filtered_schedule')
        num_pages = math.ceil(len(schedule) / num_items_per_page) # type: ignore
        current_page = min(1, num_pages)  # Replace context.user_data with query.from_user
        # await state.update_data({'num_items_per_page': num_items_per_page})
        await update_schedule_message(query.message, state, current_page, num_pages)  # Pass query.from_user to update_schedule_message # type: ignore

    elif query.data == 'filter_game':
        await state.set_state(ConversationStates.FILTER)
        logger.info("Edit Filters")
        # schedule = await load_schedule(state)
        await filter_game(query.message, state) # type: ignore
    
    elif query.data == 'lottery':
        await state.set_state(ConversationStates.LOTTERY_MENU)
        logger.info("LOTTERY!")
        await lottery_menu(query, state)

    logger.info("main_menu DONE")


@form_router.callback_query(ConversationStates.LOTTERY_MENU)
async def lottery_callback(query: types.CallbackQuery, state: FSMContext) -> None:
    state_data = await state.get_data()

    if query.data == 'back_to_menu':

        await state.set_state(ConversationStates.MAIN_MENU)
        city = state_data.get('city')
        await main_menu_message(query, city)

    elif query.data == 'profile':

        # await state.set_state(Profile.Start)
        await state.set_state(ProfileState.team_name)
        await start_profile_editing(query.message, state) # type: ignore

    elif query.data == 'show_profile':

        # await state.set_state(Profile.Start)
        await state.set_state(ProfileState.show_profile)
        await show_profile(query.message, state) # type: ignore
    
    elif query.data == 'lottery_join':
        await state.set_state(ConversationStates.LOTTERY_GAMES)
        await lottery_request(query.message, state) # type: ignore
        # await start_profile_editing(query.message, state) # temporarily


@form_router.callback_query(ConversationStates.LOTTERY_GAMES)
async def lottery_teams_callback(query: types.CallbackQuery, state: FSMContext) -> None:
    state_data = await state.get_data()
    profile_data = state_data.get('profile_data')
    teams = profile_data.get('team_name') # type: ignore

    builder = InlineKeyboardBuilder()

    builder.add(
        *[
            InlineKeyboardButton(text=team, 
                                callback_data=query.data + f"_{i}") for i, team in enumerate(teams) # type: ignore
        ]
    )

    builder.adjust(len(teams))
    await query.message.edit_text(text = f"Выберите команду:\n",  # type: ignore
                        reply_markup=builder.as_markup())
    await state.set_state(ConversationStates.LOTTERY_FINISH)

@form_router.callback_query(ConversationStates.LOTTERY_FINISH)
async def lottery_send_callback(query: types.CallbackQuery, state: FSMContext) -> None:
    game_local_id, team_id = [int(i) for i in query.data.split('_')] # type: ignore
    state_data = await state.get_data()
    schedule = state_data.get('schedule')
    city = state_data.get('city')
    
    profile_data = state_data.get('profile_data')

    today_schedule = filter_today_games(schedule, city) # type: ignore
    game_id = today_schedule[game_local_id].get('url_suf').split('=')[-1] # type: ignore

    formdata = FormData()

    for k, v in profile_data.items(): # type: ignore
        if k != 'team_name':
            formdata.add_field(LOTTERY_FIELDS.get(k), v) # type: ignore
        else:
            formdata.add_field(LOTTERY_FIELDS.get(k), v[team_id]) # type: ignore

    formdata.add_field('game_id', game_id)
    logger.info(f"Lottery DATA:\n{profile_data}")
    # formdata.add_field('game_id', 3)

    url = LOTTERY_URL
    message = query.message

    logger.info(f"LOTTERY_URL: {url}")
    logger.info(f"LOTTERY_DATA: {formdata}")
    # with open("file_id_dict.json", "r") as outfile:
    #     file_id_dict = json.load(outfile)
    # sent_message = await message.answer_photo(photo=file_id_dict["69"])
    # await message.delete()
    # message = sent_message
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://quizplease.ru/',
    }

    lottery_id = -1
    async with ClientSession() as session:
    
        async with session.post(url, data=formdata, headers=headers) as response:
                logger.info(f"Response: {response}")
                response_data = await response.json()
                if response_data.get('success'):
                    lottery_id = response_data.get('message')
                    logger.info(f"Form submitted successfully! Message: {lottery_id}")
                else:
                    logger.error(f"Failed to submit the form. Message: {response_data.get('message')}")
                    response_message = response_data.get('message')

                    await message.edit_text( # type: ignore
                        text=f"{response_message.split('<br>')[0]}",
                        parse_mode=ParseMode.HTML
                        )

    # lottery_id = '1' # for testing
    if int(lottery_id) != -1:
        if (int(lottery_id) <= 400):
            with open("file_id_dict.json", "r") as outfile:
            # with open("file_id_dict_test.json", "r") as outfile:
                file_id_dict = json.load(outfile)
            sent_message = await message.answer_photo(photo=file_id_dict[lottery_id])
            await message.delete()
            message = sent_message
        else:
            await message.edit_text(f"Успех! Ваш счастливый номер: {lottery_id}") # type: ignore
    
    new_message = await query.message.answer(text=f"Ваш город всё ещё {get_city_name(city=city)}.\n" # type: ignore
                        "Вот ваше меню:", reply_markup=main_menu_keyboard(city)) # type: ignore
    await state.update_data(actual_message = new_message)
    await state.set_state(ConversationStates.MAIN_MENU)


@form_router.callback_query(ConversationStates.PAGES)
async def button_callback(query: types.CallbackQuery, state: FSMContext):
    logger.info("button_callback STARTED")

    state_data = await state.get_data()
    # num_items_per_page =  state_data.get('num_items_per_page')  # Replace context.user_data with query.from_user

    if query.data.startswith("prev_") or query.data.startswith("next_"): # type: ignore
        action, new_page, num_pages = query.data.split("_") # type: ignore
        new_page = int(new_page)
        num_pages = int(num_pages)

        if 0 <= new_page <= num_pages:

            await state.update_data({'page': new_page})
            current_page = new_page
            await update_schedule_message(query.message, state, current_page, num_pages)   # type: ignore

    elif query.data == "schedule":
        current_page = 1  # Assuming you want to reset to the first page
        num_pages = math.ceil(len(state_data.get('schedule')) / num_items_per_page)  # type: ignore # Replace context.user_data with query.from_user
        await update_schedule_message(query.message, state, current_page, num_pages)   # type: ignore

    elif query.data == "something":
        await query.message.answer("You chose 'Something'.")  # type: ignore
    
    elif query.data == "back_to_menu":
        await state.set_state(ConversationStates.MAIN_MENU)
        city = state_data.get('city')
        await main_menu_message(query, city)
    
    logger.info("button_callback DONE")

