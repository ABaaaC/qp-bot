#!/usr/bin/env python

import logging

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

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
        rf"Hi {user.mention_html()}! This is your quiz bot.",
    )

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text("This bot provides quiz information.")

def fetch_quiz_data() -> str:
    # Fetch quiz data from "quizplease.ru" and return a sample response
    return "Question: What is the capital of France?\nOptions:\nA. Paris\nB. London\nC. Berlin\nD. Rome"

def quiz(update: Update, context: CallbackContext) -> None:
    """Send a quiz question when the command /quiz is issued."""
    quiz_data = fetch_quiz_data()
    update.message.reply_text(quiz_data)

def main() -> None:
    """Start the bot."""
    updater = Updater(token=BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # On different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("quiz", quiz))

    # Run the bot until the user presses Ctrl-C
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
