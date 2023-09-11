import asyncio
from aiogram import Bot, Dispatcher, types, F, Router
# from aiogram.contrib.middlewares.logging import LoggingMiddleware
# from aiogram.utils import executor
# from aiogram.fsm_storage.memory import MemoryStorage

from aiogram.fsm.storage.memory import MemoryStorage

from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder

from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)


from dotenv import dotenv_values
config = dotenv_values(".env")
BOT_TOKEN = config.get("BOT_TOKEN")

form_router = Router()


class Form(StatesGroup):
    team_name = State()
    name = State()
    email = State()
    phone = State()
    date_of_birth_day = State()
    date_of_birth_month = State()
    date_of_birth_year = State()
    gender = State()

@form_router.message(CommandStart())
async def cmd_start(message: Message):
    markup = ReplyKeyboardMarkup(
        text="Edit Profile",
        resize_keyboard=True, 
        selective=True,
        keyboard=[
                [
                    KeyboardButton(text="Edit Profile"),
                ]
            ])
    # markup.add()
    await message.answer("Welcome! Click 'Edit Profile' to edit your profile.", reply_markup=markup)

@form_router.message(lambda message: message.text == 'Edit Profile')
async def enter_test(message: Message, state: FSMContext):
    # await Form.team_name.set()
    await state.set_state(Form.team_name)
    await message.reply("Please enter your Team Name:", reply_markup=ReplyKeyboardRemove())

@form_router.message(Form.team_name)
async def answer_team_name(message: Message, state: FSMContext):
    await state.update_data(team_name=message.text)
    # await Form.next()
    await state.set_state(Form.name)
    await message.reply("Please enter your Name:")

@form_router.message(Form.name)
async def answer_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    # await Form.next()
    await state.set_state(Form.email)
    await message.reply("Please enter your email:")

@form_router.message(Form.email)
async def answer_name(message: Message, state: FSMContext):
    await state.update_data(email=message.text)
    # await Form.next()
    await state.set_state(Form.phone)
    await message.reply("Please enter your phone:")

@form_router.message(Form.phone)
async def answer_name(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    # await Form.next()
    await state.set_state(Form.date_of_birth_day)
    await message.reply("Please enter your date_of_birth_day:")

@form_router.message(Form.date_of_birth_day)
async def answer_name(message: Message, state: FSMContext):
    await state.update_data(date_of_birth_day=message.text)
    # await Form.next()
    await state.set_state(Form.date_of_birth_month)
    await message.reply("Please enter your date_of_birth_month:")

@form_router.message(Form.date_of_birth_month)
async def answer_name(message: Message, state: FSMContext):
    await state.update_data(date_of_birth_month=message.text)
    # await Form.next()
    await state.set_state(Form.date_of_birth_year)
    await message.reply("Please enter your date_of_birth_year:")

@form_router.message(Form.date_of_birth_year)
async def answer_name(message: Message, state: FSMContext):
    await state.update_data(date_of_birth_year=message.text)
    # await Form.next()
    await state.set_state(Form.gender)
    await message.reply("Please enter your gender:")


@form_router.message(Form.gender)
async def answer_gender(message: types.Message, state: FSMContext):
    await state.update_data(gender=message.text)
    data = await state.get_data()
    await message.reply(f"Your Profile:\n"
                        f"Team Name: {data['team_name']}\n"
                        f"Name: {data['name']}\n"
                        f"Email: {data['email']}\n"
                        f"Phone: {data['phone']}\n"
                        f"Date of Birth: {data['date_of_birth_day']}/{data['date_of_birth_month']}/{data['date_of_birth_year']}\n"
                        f"Gender: {data['gender']}", parse_mode=ParseMode.MARKDOWN)
    # await state.finish()

async def main():
    bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    
    dp.include_router(form_router)

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
    
