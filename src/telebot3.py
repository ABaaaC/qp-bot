#!/usr/bin/env python

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

# Replace 'YOUR_BOT_TOKEN' with the token you received from BotFather
BOT_TOKEN = '6521875912:AAGsFRaaEv3OMtb8apHfyayMFdPv6uT1foQ'

# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_html(
        rf"Hi {user.mention_html()}! This is your quiz bot. Send /quiz to get a quiz question.",
    )

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text("This bot provides quiz information. Send /quiz to get a quiz question.")

def fetch_quiz_data() -> dict:
    # Fetch quiz data from "quizplease.ru" and return a sample response
    return {
        "question": "What is the capital of France?",
        "options": ["Paris", "London", "Berlin", "Rome"],
    }

def quiz(update: Update, context: CallbackContext) -> None:
    """Send a quiz question when the command /quiz is issued."""
    quiz_data = fetch_quiz_data()
    question = quiz_data["question"]
    options = quiz_data["options"]
    
    keyboard = [
        [InlineKeyboardButton(option, callback_data=option)] for option in options
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.message.reply_text(
        f"Question: {question}",
        reply_markup=reply_markup
    )

def button_callback(update: Update, context: CallbackContext) -> None:
    """Handle button clicks."""
    selected_option = update.callback_query.data
    update.callback_query.answer(f"You selected: {selected_option}")

def main() -> None:
    """Start the bot."""
    updater = Updater(token=BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("quiz", quiz))
    dispatcher.add_handler(MessageHandler(Filters.text, button_callback))  # Handle button clicks

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
