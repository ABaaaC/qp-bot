
# from src.schedule_parser import extract_schedule
from src.schedule_loader import read_or_download_schedule
from dotenv import dotenv_values
config = dotenv_values(".env")
BOT_TOKEN = config["BOT_TOKEN"]
#!/usr/bin/env python

import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
import math

# Define the number of items per page
num_items_per_page = 5

# Enable logging
# logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
# logger = logging.getLogger(__name__)

# clrd_fmt = '\x1b[38;5;226m' + '%(levelname)s' + ': %(name)s - (%(asctime)s)' + ' \t\x1b[0m %(message)s'
# logging.basicConfig(level=logging.INFO, format=clrd_fmt)
# logger = logging.getLogger(__name__)

fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
clrd_fmt = '\x1b[38;5;226m' + fmt + '\x1b[0m'
logging.basicConfig(format=clrd_fmt, level=logging.INFO, )
logger = logging.getLogger(__name__)

# Conversation states
CITY_CHOICE, MAIN_MENU = range(2)

def start(update: Update, context: CallbackContext) -> int:
    logger.info("start")
    custom_keyboard = [[KeyboardButton("Moscow")]]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True, one_time_keyboard=True)
    update.message.reply_text("Please choose a city:", reply_markup=reply_markup)
    return CITY_CHOICE

def city_choice(update: Update, context: CallbackContext) -> int:
    logger.info("city_choice")
    context.user_data['city'] = update.message.text
    update.message.reply_text(f"Great! You chose {context.user_data['city']}.\n"
                              "Now, please choose an option from the main menu:",
                              reply_markup=main_menu_keyboard())
    return MAIN_MENU

def main_menu_keyboard() -> InlineKeyboardMarkup:
    logger.info("main_menu_keyboard")
    keyboard = [
        [InlineKeyboardButton("Schedule", callback_data="schedule"),
        InlineKeyboardButton("Something", callback_data="something")]
    ]
    return InlineKeyboardMarkup(keyboard)

def main_menu(update: Update, context: CallbackContext) -> int:
    logger.info("main_menu")
    query = update.callback_query
    query.answer()

    if query.data == "schedule":
        logger.info("Reading or Downloading Schedule")
        schedule = read_or_download_schedule("https://moscow.quizplease.ru/schedule", expiration_hours = 24)
        logger.info("Done!")
        context.user_data['schedule'] = schedule
        context.user_data['page'] = 0
        current_page = context.user_data['page'] + 1
        num_pages = math.ceil(len(schedule) / num_items_per_page)
        update_schedule_message(query.message, context, current_page, num_pages)

    elif query.data == "something":
        query.message.reply_text("You chose 'Something'.")
    
    elif query.data == "back_to_menu":
        query.edit_message_text(f"Great! You chose {context.user_data['city']}.\n"
        "Now, please choose an option from the main menu:",
        reply_markup=main_menu_keyboard())

    return MAIN_MENU

def update_schedule_message(message, context, current_page, num_pages):
    logger.info("update_schedule_message")
    schedule = context.user_data['schedule']
    start_index = (current_page - 1) * num_items_per_page
    end_index = min(start_index + num_items_per_page, len(schedule))

    schedule_text = "\n".join([f"{i + 1 + start_index}. {item['title']} - {item['date']} at {item['time']}" for i, item in enumerate(schedule[start_index:end_index])])
    keyboard = []

    if start_index > 0:
        keyboard.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"prev_{current_page - 1}_{num_pages}"))

    keyboard.append(InlineKeyboardButton("🔙 Back", callback_data="back_to_menu"))

    if end_index < len(schedule):
        keyboard.append(InlineKeyboardButton("➡️ Next", callback_data=f"next_{current_page + 1}_{num_pages}"))

    message_text = f"Here is the schedule for your chosen city (Page {current_page}/{num_pages}):\n{schedule_text}"
    message.edit_text(message_text, reply_markup=InlineKeyboardMarkup([keyboard]))

def button_callback(update: Update, context: CallbackContext) -> None:
    logger.info("button_callback")
    query = update.callback_query
    query.answer()
    num_items_per_page = context.user_data.get('num_items_per_page', 5)

    if query.data.startswith("prev_") or query.data.startswith("next_"):
        action, new_page, num_pages = query.data.split("_")
        new_page = int(new_page)
        num_pages = int(num_pages)

        if 0 <= new_page <= num_pages:
            context.user_data['page'] = new_page
            current_page = new_page
            update_schedule_message(query.message, context, current_page, num_pages)

    elif query.data == "schedule":
        current_page = 1  # Assuming you want to reset to the first page
        num_pages = math.ceil(len(context.user_data['schedule']) / num_items_per_page)
        update_schedule_message(query.message, context, current_page, num_pages)

    elif query.data == "something":
        query.edit_message_text("You chose 'Something'.")

    elif query.data == "back_to_menu":

        query.edit_message_text(f"Great! You chose {context.user_data['city']}.\n"
        "Now, please choose an option from the main menu:",
        reply_markup=main_menu_keyboard())
      
def main() -> None:
    """Start the bot."""
    updater = Updater(token=BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CITY_CHOICE: [MessageHandler(Filters.text & ~Filters.command, city_choice)],
            MAIN_MENU: [CallbackQueryHandler(main_menu, pattern='^(schedule|something)$'),
                        CallbackQueryHandler(button_callback)],
        },
        fallbacks=[],
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
