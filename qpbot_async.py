from fastapi import FastAPI, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from telegram import Update
from telegram.ext import Dispatcher, CallbackContext
import os, logging
import uvicorn

from src.pygramtic_models import Update as TelegramUpdate, Message, Chat, InlineQuery, User, Location, \
    ChosenInlineResult, CallbackQuery, ShippingQuery, PreCheckoutQuery, Poll, \
    ShippingAddress, OrderInfo, PollOption, MessageEntity, Audio, Document, Animation, \
    Game, PhotoSize, Sticker, Voice, Video, VideoNote, Contact, Venue, Invoice, \
    SuccessfulPayment, InlineKeyboardMarkup, PassportData, MaskPosition, \
    EncryptedPassportElement, EncryptedCredentials, PassportFile, InlineKeyboardButton, \
    LoginUrl, CallbackGame

from dotenv import dotenv_values
config = dotenv_values(".env")
# BOT_TOKEN = config["BOT_TOKEN"]
BOT_TOKEN = config.get("BOT_TOKEN")


from pydantic import BaseModel
from typing import Optional, List

# fmt = "%(levelname)s - %(message)s"
clrd_fmt = '\x1b[38;5;226m' + '%(levelname)s' + ': %(name)s - (%(asctime)s)' + ' \t\x1b[0m %(message)s'
logging.basicConfig(level=logging.INFO, format=clrd_fmt)
logger = logging.getLogger(__name__)

from src.telebot9 import updater, dispatcher as dp  # Import the Updater instance
from src.telebot9 import main as start_telegram_bot
# from src.modified2_telebot9_final import updater  # Import the Updater instance
# from src.modified2_telebot9_final import main as start_telegram_bot

app = FastAPI()

# Dependency to get the dispatcher and update queue
# def get_dispatcher_queue():
#     # Get the dispatcher and update queue from the Updater instance
#     dispatcher = updater.dispatcher
#     update_queue = updater.update_queue
#     return dispatcher, update_queue


# @app.on_event("startup")
# async def on_startup():
#     webhook_info = await bot.get_webhook_info()
#     if webhook_info.url != WEBHOOK_URL:
#         await bot.set_webhook(
#             url=WEBHOOK_URL
#         )

# @dp.(commands=['start'])
# async def start_handler(message: Message):
#     user_id = message.from_user.id
#     user_full_name = message.from_user.full_name
#     logger.info("KEK, //start handled")
#     await message.reply(f"Hello, {user_full_name}!")


@app.on_event("startup")
async def startup_event() -> None:
    try:
        logger.info(f"StartUp")
        # webhook_url = "https://qp-bot.onrender.com/webhook/6521875912:AAG-a7eTLXEC_6JJupnLpQ3STTuYD-gyhME"
        # webhook_url = f"https://curious-frequently-katydid.ngrok-free.app/webhook/{BOT_TOKEN}"
        webhook_url = f"https://curious-frequently-katydid.ngrok-free.app/webhook/{BOT_TOKEN}"
        updater.bot.setWebhook(webhook_url)
        # updater.start_webhook(
        #     webhook_url=webhook_url,
        #     port=8080,
        #     url_path=f"webhook/{BOT_TOKEN}"
        #     )
    except Exception as e:
        logging.critical(f"Error occurred while starting up app: {e}")

@app.post("/webhook/{token}", response_model=None)
async def webhook(token: str, update: TelegramUpdate):
    # logger.info(f"Incoming update: {update.dict()}")
    logger.info(f"Incoming update: {update.model_dump().keys()}")
    # Validate the token here if needed
    if token != BOT_TOKEN:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    # Put the incoming update into the update queue
    # updater.update_queue.put(update.model_dump())
    logger.info(f"Started?")
    start_telegram_bot()
    logger.info(f"Started!")
    updater.update_queue.put_nowait(update.model_dump())
    logger.info(updater.update_queue.qsize())
    logger.info(f"Message received!")

    # await updater.dispatcher.start()
    return {"status": "OK"}

@app.get("/")
async def main_web_handler():
    return "Everything ok!"

if __name__ == "__main__":
    # HOST = os.getenv("HOST", "0.0.0.0")
    # PORT = os.getenv("PORT", 8080)
    # uvicorn.run(app, host=HOST, port=PORT)
    HOST = os.getenv("HOST", "127.0.0.1")
    uvicorn.run(app, host=HOST, port=8080)


# https://api.telegram.org/bot6521875912:AAG-a7eTLXEC_6JJupnLpQ3STTuYD-gyhME/setWebhook?url=https://qp-bot.onrender.com/webhook/6521875912:AAG-a7eTLXEC_6JJupnLpQ3STTuYD-gyhME

# class FromModel(BaseModel):
#     id: int
#     is_bot: bool
#     first_name: str
#     username: str
#     language_code: str
#     is_premium: bool

# class ChatModel(BaseModel):
#     id: int
#     first_name: str
#     username: str
#     type: str

# class EntityModel(BaseModel):
#     offset: int
#     length: int
#     type: str

# class MessageModel(BaseModel):
#     message_id: int
#     from_user: FromModel
#     chat: ChatModel
#     date: int
#     text: str
#     entities: list[EntityModel]

# class UpdateModel(BaseModel):
#     update_id: int
#     message: MessageModel

