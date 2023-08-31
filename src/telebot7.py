
# from schedule_parser import extract_schedule
BOT_TOKEN = '6521875912:AAGsFRaaEv3OMtb8apHfyayMFdPv6uT1foQ'
#!/usr/bin/env python

import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
import math

# Define the number of items per page
num_items_per_page = 5

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Conversation states
CITY_CHOICE, MAIN_MENU = range(2)

def start(update: Update, context: CallbackContext) -> int:
    custom_keyboard = [[KeyboardButton("Moscow")]]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True, one_time_keyboard=True)
    update.message.reply_text("Please choose a city:", reply_markup=reply_markup)
    return CITY_CHOICE

def city_choice(update: Update, context: CallbackContext) -> int:
    context.user_data['city'] = update.message.text
    update.message.reply_text(f"Great! You chose {context.user_data['city']}.\n"
                              "Now, please choose an option from the main menu:",
                              reply_markup=main_menu_keyboard())
    return MAIN_MENU

def main_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("Schedule", callback_data="schedule"),
        InlineKeyboardButton("Something", callback_data="something")]
    ]
    return InlineKeyboardMarkup(keyboard)

def main_menu(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()

    if query.data == "schedule":
        schedule = extract_schedule("https://moscow.quizplease.ru/schedule")
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


def extract_schedule(url: str) -> list:
    # Implement your logic to extract schedule from the URL and return the list
    # Each item in the list should be a dictionary with 'date', 'title', 'package_number', 'time', and 'place' fields
    # For example:
    import json
    with open("schedule_example.json", "r") as json_file:
        schedule = json.load(json_file)
    return schedule

def button_callback(update: Update, context: CallbackContext) -> None:
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
        # print("\n".join(dir(update)))
        # print(update.callback_query)
        query.edit_message_text(f"Great! You chose {context.user_data['city']}.\n"
        "Now, please choose an option from the main menu:",
        reply_markup=main_menu_keyboard())
        # update.message.edit_text(f"Great! You chose {context.user_data['city']}.\n"
        #                     "Now, please choose an option from the main menu:",
        #                     reply_markup=main_menu_keyboard())
        # update_schedule_message(query.message, context, current_page, num_pages)


        

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
