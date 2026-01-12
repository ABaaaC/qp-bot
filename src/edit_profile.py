from venv import logger
from aiogram import Router, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.enums import ParseMode

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
)

from src.gdrive import change_profile_on_gdrive

from src.consts import (
    ProfileEdit,
    ProfileState,
    ConversationStates,
    loto_profiles
)

from src.pages.utils import filter_today_games

import phonenumbers
import re
from datetime import datetime
import calendar

# form_router = Router()
# from src.telebot10_aio import form_router, BOT_TOKEN
form_router = Router()




async def return_actual_message(message: Message, state: FSMContext):
    await message.delete()
    state_data = await state.get_data()
    message = state_data.get('actual_message') # type: ignore
    # message = bot.mess
    return message

# @form_router.message(lambda message: message.text == 'Edit Profile')
async def enter_test(message: Message, state: FSMContext):
    # await ProfileState.team_name.set()
    await message.edit_text("Ваша команда (можно несколько в разных строках):")
    current_state = await state.get_state()
    if current_state != ProfileEdit.team_name: 
        await state.set_state(ProfileState.team_name)

@form_router.message(ProfileEdit.team_name)
@form_router.message(ProfileState.team_name)
async def answer_team_name(message: Message, state: FSMContext):

    current_state = await state.get_state()

    state_data = await state.get_data()
    profile_data = state_data.get('profile_data', dict()) if state_data.get('profile_data') is not None else dict()
    teams = message.text.split('\n') # type: ignore
    profile_data.update(team_name=teams)
    await state.update_data(profile_data=profile_data)

    message = await return_actual_message(message, state)

    if current_state == ProfileEdit.team_name: 
        await state.set_state(ProfileState.show_profile)
        await show_profile(message, state)
    elif current_state == ProfileState.team_name: 
        await state.set_state(ProfileState.name)
        await message.edit_text("Введите имя:")

@form_router.message(ProfileState.name)
@form_router.message(ProfileEdit.name)
async def answer_name(message: Message, state: FSMContext):

    current_state = await state.get_state()

    state_data = await state.get_data()
    profile_data = state_data.get('profile_data')
    profile_data.update(name=message.text) # type: ignore
    await state.update_data(profile_data=profile_data)

    message = await return_actual_message(message, state)

    if current_state == ProfileEdit.name: 
        await state.set_state(ProfileState.show_profile)
        await show_profile(message, state)
    elif current_state == ProfileState.name: 
        await state.set_state(ProfileState.email)
        await message.edit_text("Ваш e-mail:")

@form_router.message(ProfileState.email)
@form_router.message(ProfileEdit.email)
async def answer_email(message: Message, state: FSMContext):

    current_state = await state.get_state()

    email_str = message.text
    pattern = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
    valid_flag = bool(pattern.match(email_str)) # type: ignore

    # valid_flag = True
    if valid_flag:
        state_data = await state.get_data()
        profile_data = state_data.get('profile_data')
        profile_data.update(email=message.text) # type: ignore
        await state.update_data(profile_data=profile_data)

        # await state.update_data(email=message.text)

        message = await return_actual_message(message, state)

        if ProfileEdit.email == current_state: 
            await state.set_state(ProfileState.show_profile)
            await show_profile(message, state)
        elif ProfileState.email == current_state: 
            await state.set_state(ProfileState.phone)
            await message.edit_text("Номер телефона:")

    else:

        message = await return_actual_message(message, state)
        await message.edit_text("Введите настоящий email:")
    
@form_router.message(ProfileState.phone)
@form_router.message(ProfileEdit.phone)
async def answer_phone(message: Message, state: FSMContext):

    current_state = await state.get_state()

    phone_number_str = message.text
    try:
        phone_number = phonenumbers.parse(phone_number_str) # type: ignore
        valid_flag = phonenumbers.is_valid_number(phone_number)
    except phonenumbers.NumberParseException:
        valid_flag = False
    
    if valid_flag:

        phone = phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.E164) # type: ignore

        state_data = await state.get_data()
        profile_data = state_data.get('profile_data')
        profile_data.update(phone=phone) # type: ignore
        await state.update_data(profile_data=profile_data)

        # await state.update_data(phone=message.text)

        message = await return_actual_message(message, state)

        if current_state == ProfileEdit.phone: 
            await state.set_state(ProfileState.show_profile)
            await show_profile(message, state)
        elif current_state == ProfileState.phone: 

            await state.set_state(ProfileState.date_of_birth_year)
            await message.edit_text("Введите год вашего рождения:")

    else:
        message = await return_actual_message(message, state)
        await message.edit_text("Введите существующий номер телефона:")

@form_router.message(ProfileState.date_of_birth_year)
@form_router.message(ProfileEdit.date_of_birth_year)
async def answer_date_of_birth_year(message: Message, state: FSMContext):
    # await state.update_data(date_of_birth_year=message.text)
    current_state = await state.get_state()

    current_year = datetime.now().year

    valid_flag = message.text.isdigit() and (1900 < int(message.text) < current_year)  # type: ignore
    
    
    # valid_flag = True
    if valid_flag:
        state_data = await state.get_data()
        profile_data = state_data.get('profile_data')
        profile_data.update(date_of_birth_year=message.text) # type: ignore
        await state.update_data(profile_data=profile_data)

        message = await return_actual_message(message, state)

        if current_state == ProfileEdit.date_of_birth_year: 
            await state.set_state(ProfileEdit.date_of_birth_month)
        if current_state == ProfileState.date_of_birth_year: 
            await state.set_state(ProfileState.date_of_birth_month)

        await message.edit_text("Номер месяца рождения:")
    else:
        message = await return_actual_message(message, state)
        await message.edit_text("Введите корректный год рождения")

@form_router.message(ProfileState.date_of_birth_month)
@form_router.message(ProfileEdit.date_of_birth_month)
async def answer_date_of_birth_month(message: Message, state: FSMContext):
    # await state.update_data(date_of_birth_month=message.text)
    current_state = await state.get_state()

    valid_flag = message.text.isdigit() and (1 <= int(message.text) <= 12) # type: ignore
    
    # valid_flag = True

    if valid_flag:
        state_data = await state.get_data()
        profile_data = state_data.get('profile_data')
        profile_data.update(date_of_birth_month=message.text) # type: ignore
        await state.update_data(profile_data=profile_data)

        message = await return_actual_message(message, state)

        if current_state == ProfileEdit.date_of_birth_month: 
            await state.set_state(ProfileEdit.date_of_birth_day)
            current_state = await state.get_state()
        if current_state == ProfileState.date_of_birth_month: 
            await state.set_state(ProfileState.date_of_birth_day)
            current_state = await state.get_state()

        await message.edit_text("День рождения:")


        year = profile_data.get('date_of_birth_year') # type: ignore
        month = profile_data.get('date_of_birth_month') # type: ignore
        _, days_in_month = calendar.monthrange(int(year), int(month))

        builder = InlineKeyboardBuilder()

        builder.add(
            *[
                InlineKeyboardButton(text=f"{i}", callback_data=f"day_{i}") for i in range(1, days_in_month + 1)
            ]
        )

        builder.adjust(5)


        await message.edit_reply_markup(
                text = "День рождения:",
                reply_markup=builder.as_markup()
            )
        
        if current_state == ProfileEdit.date_of_birth_day: 
            # await state.set_state(ProfileState.show_profile)
            # await show_profile(message, state)
            pass
        elif current_state == ProfileState.date_of_birth_day: 
            await state.set_state(ProfileState.gender)
    else:

        message = await return_actual_message(message, state)
        await message.edit_text("Введите корректный номер месяца")

@form_router.callback_query(ProfileState.date_of_birth_day)
@form_router.callback_query(ProfileEdit.date_of_birth_day)
async def answer_date_of_birth_day(query: CallbackQuery, state: FSMContext):

    # await state.update_data(date_of_birth_day=message.text)
    message = query.message
    current_state = await state.get_state()

    state_data = await state.get_data()
    profile_data = state_data.get('profile_data')

    if query.data.split('_')[0] == 'day':
        day = query.data.split('_')[1]

        profile_data.update(date_of_birth_day=day) # type: ignore
        await state.update_data(profile_data=profile_data)

        await state.set_state(ProfileState.show_profile)
        await show_profile(query.message, state)

    else:
        year = profile_data.get('date_of_birth_year') # type: ignore
        month = profile_data.get('date_of_birth_month') # type: ignore

        _, days_in_month = calendar.monthrange(int(year), int(month))


        valid_flag = message.text.isdigit() and (1 <= int(message.text) <= days_in_month) # type: ignore

        valid_flag = True

        if valid_flag:
            # profile_data.update(date_of_birth_day=message.text) # type: ignore
            profile_data.update(date_of_birth_day=query.data) # type: ignore
            await state.update_data(profile_data=profile_data)

            message = await return_actual_message(message, state)

            if current_state == ProfileEdit.date_of_birth_day: 
                await state.set_state(ProfileState.show_profile)
                await show_profile(message, state)
            elif current_state == ProfileState.date_of_birth_day: 
                await state.set_state(ProfileState.gender)
                await message.edit_reply_markup(
                        text = "Выберите ваш пол:",
                        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                            [
                                InlineKeyboardButton(text='М', callback_data='0'),
                                InlineKeyboardButton(text='Ж', callback_data='1')
                            ]
                        ])
                    )


        else:

            message = await return_actual_message(message, state)
            await message.edit_text("Введите корректный номер дня")

# @form_router.message(ProfileState.gender)
@form_router.callback_query(ProfileState.gender)
@form_router.callback_query(ProfileEdit.gender)
async def answer_gender(query: CallbackQuery, state: FSMContext):

    state_data = await state.get_data()
    profile_data = state_data.get('profile_data', dict())
    profile_data.update(gender=query.data)
    await state.update_data(profile_data=profile_data)

    await state.set_state(ProfileState.show_profile)
    await show_profile(query.message, state)

def profile_str(profile_data: dict) -> str:
    return f"Ваш профиль:\n" +\
        f"Имя: {profile_data['name']}\n" +\
        f"Имя команды: {', '.join(profile_data['team_name'])}\n" +\
        f"Email: {profile_data['email']}\n" +\
        f"Телефон: {profile_data['phone']}\n" +\
        f"День рождения: {profile_data['date_of_birth_day']}/{profile_data['date_of_birth_month']}/{profile_data['date_of_birth_year']}\n" +\
        f"Пол: {'Ж' if profile_data['gender'] == '1' else 'М'}"

@form_router.callback_query(ProfileState.show_profile)
async def correction_profile(query: CallbackQuery, state: FSMContext):
    logger.info("profile correction started")
    if query.data == "team_name":
        await state.set_state(ProfileEdit.team_name)
        await enter_test(query.message, state)

    elif query.data == "name":
        await state.set_state(ProfileEdit.name)
        await query.message.edit_text("Введите имя:")

    elif query.data == "email":
        await state.set_state(ProfileEdit.email)
        await query.message.edit_text("Ваш e-mail:")

    elif query.data == "phone":
        await state.set_state(ProfileEdit.phone)
        await query.message.edit_text("Номер телефона:")

    elif query.data == "birthday":
        await state.set_state(ProfileEdit.date_of_birth_year)
        await query.message.edit_text("Введите год вашего рождения:")

    elif query.data == "gender":
        await state.set_state(ProfileEdit.gender)
        await query.message.edit_text("Выберите ваш пол:")

        await query.message.edit_reply_markup(
                text = "Выберите ваш пол:",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(text='М', callback_data='0'),
                        InlineKeyboardButton(text='Ж', callback_data='1')
                    ]
                ])
            )

    elif query.data == "back_to_menu":
        await state.set_state(ConversationStates.LOTTERY_MENU)
        await lottery_menu(query, state)

async def lottery_request(message: Message, state: FSMContext) -> None:
    state_data = await state.get_data()
    profile_data = state_data.get('profile_data')
    schedule = state_data.get('schedule')
    city = state_data.get('city')

    # logger.info(schedule)

    today_schedule = filter_today_games(schedule, city) # type: ignore

    # logger.info(today_schedule)

    builder = InlineKeyboardBuilder()

    game_texts = "\n".join([f"{i+1}. {item.get('title')}, #{item.get('package_number')}, {item.get('place')}, {item.get('datetime')}"  
                            for i, item in enumerate(today_schedule)])
    builder.add(
        *[
            # InlineKeyboardButton(text=f"{i+1}", callback_data=f"enter_lottery_{i+1}") \
            InlineKeyboardButton(text=f"{i+1}", callback_data=f"{i}") \
                                for i in range(len(today_schedule))
        ]
    )

    builder.adjust(len(today_schedule))
    await message.edit_text(text = f"Выберите игру для лотереи:\n"+game_texts,
                        reply_markup=builder.as_markup()) # type: ignore

def lottery_menu_keyboard(profile_exists: bool) -> InlineKeyboardMarkup:
    if  profile_exists:
    # if  True:
        keyboard = [
            [
                InlineKeyboardButton(text = "Посмотреть Профиль 🌝", callback_data="show_profile"),
            ],
            [
                InlineKeyboardButton(text = "Участвовать 🚀", callback_data='lottery_join'),
            ],
            [
                InlineKeyboardButton(text = "🔙 Назад", callback_data="back_to_menu"),
            ]
        ]
    else:
        keyboard = [
            [
                InlineKeyboardButton(text = "Создать Профиль ✏️", callback_data="profile"),
                InlineKeyboardButton(text = "🔙 Назад", callback_data="back_to_menu"),
            ]
        ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

async def show_profile(message: Message, state: FSMContext):
    # await ProfileState.team_name.set()
    state_data = await state.get_data()
    profile_data = state_data.get('profile_data', dict())

    user_id = str(message.chat.id)
    saved_profile = loto_profiles.get(user_id)

    if saved_profile == profile_data:
        logger.info("PROFILES EQs")
    else:
        logger.info("PROFILES not EQs")
        change_profile_on_gdrive(user_id, profile_data)




    profile = profile_str(profile_data)
    profile = profile + "\n\nПодредактировать?"

    keyboard = [
        [
        InlineKeyboardButton(text = "Команду", callback_data="team_name"),
        # ],[
        InlineKeyboardButton(text = "Номер Телефона", callback_data="phone"),
        ],[
        InlineKeyboardButton(text = "Имя", callback_data="name"),
        # ],[
        InlineKeyboardButton(text = "День Рождения", callback_data="birthday"),
        ],[
        InlineKeyboardButton(text = "email", callback_data="email"),
        # ],[
        InlineKeyboardButton(text = "Пол (🌚)", callback_data="gender"),        
        ],[

        InlineKeyboardButton(text = "🔙 Назад", callback_data="back_to_menu"),
        ]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)


    await message.edit_text(profile, reply_markup=markup)

async def lottery_menu(query: CallbackQuery, state: FSMContext) -> None:
    state_data = await state.get_data()
    profile_data = state_data.get('profile_data')

    markup = lottery_menu_keyboard(profile_data is not None)
    await query.message.edit_text("Выберите:", reply_markup=markup) # type: ignore
    # await query.message.edit_reply_markup(reply_markup=lottery_menu_keyboard(profile_data is not None)) # type: ignore,