from aiogram import Router
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

import phonenumbers
import re
from datetime import datetime
import calendar

# form_router = Router()
# from src.telebot10_aio import form_router, BOT_TOKEN
form_router = Router()

class ProfileState(StatesGroup):
    Start = State()
    team_name = State()
    name = State()
    email = State()
    phone = State()
    date_of_birth_day = State()
    date_of_birth_month = State()
    date_of_birth_year = State()
    gender = State()
    Finish = State()

async def return_actual_message(message: Message, state: FSMContext):
    await message.delete()
    state_data = await state.get_data()
    message = state_data.get('actual_message') # type: ignore
    # message = bot.mess
    return message

# @form_router.message(lambda message: message.text == 'Edit Profile')
async def enter_test(message: Message, state: FSMContext):
    # await ProfileState.team_name.set()
    await state.set_state(ProfileState.team_name)
    await message.edit_text("Ваша команда (можно несколько в разных строках):")

@form_router.message(ProfileState.team_name)
async def answer_team_name(message: Message, state: FSMContext):

    state_data = await state.get_data()
    profile_data = state_data.get('profile_data', dict()) if state_data.get('profile_data') is not None else dict()
    teams = message.text.split('\n') # type: ignore
    profile_data.update(team_name=teams)
    await state.update_data(profile_data=profile_data)

    message = await return_actual_message(message, state)

    await state.set_state(ProfileState.name)
    await message.edit_text("Введите имя:")

@form_router.message(ProfileState.name)
async def answer_name(message: Message, state: FSMContext):
    state_data = await state.get_data()
    profile_data = state_data.get('profile_data')
    profile_data.update(name=message.text) # type: ignore
    await state.update_data(profile_data=profile_data)

    # await state.update_data(name=message.text)

    message = await return_actual_message(message, state)

    await state.set_state(ProfileState.email)
    await message.edit_text("Ваш e-mail:")

@form_router.message(ProfileState.email)
async def answer_email(message: Message, state: FSMContext):
    email_str = message.text
    pattern = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
    valid_flag = bool(pattern.match(email_str)) # type: ignore

    valid_flag = True
    if valid_flag:
        state_data = await state.get_data()
        profile_data = state_data.get('profile_data')
        profile_data.update(email=message.text) # type: ignore
        await state.update_data(profile_data=profile_data)

        # await state.update_data(email=message.text)

        message = await return_actual_message(message, state)
    
        await state.set_state(ProfileState.phone)
        await message.edit_text("Номер телефона:")

    else:

        message = await return_actual_message(message, state)
        await message.edit_text("Введите настоящий email:")

@form_router.message(ProfileState.phone)
async def answer_phone(message: Message, state: FSMContext):
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

        await state.set_state(ProfileState.date_of_birth_year)
        await message.edit_text("Введите год вашего рождения:")

    else:
        message = await return_actual_message(message, state)
        await message.edit_text("Введите существующий номер телефона:")

@form_router.message(ProfileState.date_of_birth_year)
async def answer_date_of_birth_year(message: Message, state: FSMContext):
    # await state.update_data(date_of_birth_year=message.text)
    current_year = datetime.now().year

    valid_flag = message.text.isdigit() and (1900 < int(message.text) < current_year)  # type: ignore
    
    
    # valid_flag = True
    if valid_flag:
        state_data = await state.get_data()
        profile_data = state_data.get('profile_data')
        profile_data.update(date_of_birth_year=message.text) # type: ignore
        await state.update_data(profile_data=profile_data)

        message = await return_actual_message(message, state)

        await state.set_state(ProfileState.date_of_birth_month)

        await message.edit_text("Номер месяца рождения:")
    else:
        message = await return_actual_message(message, state)
        await message.edit_text("Введите корректный год рождения")

@form_router.message(ProfileState.date_of_birth_month)
async def answer_date_of_birth_month(message: Message, state: FSMContext):
    # await state.update_data(date_of_birth_month=message.text)

    valid_flag = message.text.isdigit() and (1 <= int(message.text) <= 12) # type: ignore
    
    # valid_flag = True

    if valid_flag:
        state_data = await state.get_data()
        profile_data = state_data.get('profile_data')
        profile_data.update(date_of_birth_month=message.text) # type: ignore
        await state.update_data(profile_data=profile_data)

        message = await return_actual_message(message, state)

        await state.set_state(ProfileState.date_of_birth_day)
        await message.edit_text("День рождения:")
    else:

        message = await return_actual_message(message, state)
        await message.edit_text("Введите корректный номер месяца")

@form_router.message(ProfileState.date_of_birth_day)
async def answer_date_of_birth_day(message: Message, state: FSMContext):
    # await state.update_data(date_of_birth_day=message.text)
    state_data = await state.get_data()
    profile_data = state_data.get('profile_data')

    year = profile_data.get('date_of_birth_year') # type: ignore
    month = profile_data.get('date_of_birth_month') # type: ignore
    _, days_in_month = calendar.monthrange(int(year), int(month))

    valid_flag = message.text.isdigit() and (1 <= int(message.text) <= days_in_month) # type: ignore

    # valid_flag = True

    if valid_flag:
        profile_data.update(date_of_birth_day=message.text) # type: ignore
        await state.update_data(profile_data=profile_data)

        message = await return_actual_message(message, state)

        await state.set_state(ProfileState.gender)
        await message.edit_text("Выберите ваш пол:")

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
async def answer_gender(query: CallbackQuery, state: FSMContext):

    state_data = await state.get_data()
    profile_data = state_data.get('profile_data', dict())
    profile_data.update(gender=query.data)
    await state.update_data(profile_data=profile_data)

    await state.set_state(ProfileState.Finish)
    builder = InlineKeyboardBuilder()
    
    builder.add(InlineKeyboardButton(text = "Сохранить", callback_data='save'))

    profile = f"Ваш профиль:\n" +\
        f"Имя: {profile_data['name']}\n" +\
        f"Имя команды: {', '.join(profile_data['team_name'])}\n" +\
        f"Email: {profile_data['email']}\n" +\
        f"Телефон: {profile_data['phone']}\n" +\
        f"День рождения: {profile_data['date_of_birth_day']}/{profile_data['date_of_birth_month']}/{profile_data['date_of_birth_year']}\n" +\
        f"Пол: {'Ж' if profile_data['gender'] == '1' else 'М'}"

    await query.message.edit_text(profile) # type: ignore
    await query.message.edit_reply_markup( # type: ignore
                        parse_mode=ParseMode.MARKDOWN,
                        reply_markup=builder.as_markup()
                        )

    
