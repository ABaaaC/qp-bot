from fastapi import FastAPI, Depends, HTTPException, Request
from pydantic import BaseModel
from telegram import Update
from telegram.ext import Dispatcher, CallbackContext
import os
import uvicorn

from dotenv import dotenv_values
config = dotenv_values(".env")
BOT_TOKEN = config["BOT_TOKEN"]

from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    id: int
    is_bot: bool
    first_name: str
    username: Optional[str]

class Chat(BaseModel):
    id: int
    type: str

class Message(BaseModel):
    message_id: int
    from_user: Optional[User]
    chat: Chat
    text: Optional[str]

class CallbackQuery(BaseModel):
    id: str
    from_user: User
    message: Message
    data: str

class Update(BaseModel):
    update_id: int
    message: Optional[Message]
    callback_query: Optional[CallbackQuery]

from src.telebot9 import updater  # Import the Updater instance

app = FastAPI()

# Dependency to get the dispatcher and update queue
def get_dispatcher_queue():
    # Get the dispatcher and update queue from the Updater instance
    dispatcher = updater.dispatcher
    update_queue = updater.update_queue
    return dispatcher, update_queue

@app.post("/webhook/{token}", response_model=None)
async def webhook(token: str, update: Update):
    # Validate the token here if needed
    if token != BOT_TOKEN:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    # Put the incoming update into the update queue
    updater.update_queue.put(update.dict())
    return {"status": "ok"}

if __name__ == "__main__":
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = os.getenv("PORT", 8080)
    uvicorn.run(app, host=HOST, port=PORT)


# https://api.telegram.org/bot6521875912:AAG-a7eTLXEC_6JJupnLpQ3STTuYD-gyhME/setWebhook?url=https://qp-bot.onrender.com/webhook/6521875912:AAG-a7eTLXEC_6JJupnLpQ3STTuYD-gyhME