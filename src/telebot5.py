
# from schedule_parser import extract_schedule
BOT_TOKEN = '6521875912:AAGsFRaaEv3OMtb8apHfyayMFdPv6uT1foQ'
#!/usr/bin/env python

import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
import math

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


# Conversation states
CITY_CHOICE, MAIN_MENU = range(2)

def start(update: Update, context: CallbackContext) -> int:
    """Start the conversation and ask the user to choose a city."""
    custom_keyboard = [
        [KeyboardButton("Moscow")],
        # You can add more city options here
    ]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True, one_time_keyboard=True)

    update.message.reply_text("Please choose a city:", reply_markup=reply_markup)

    return CITY_CHOICE

def city_choice(update: Update, context: CallbackContext) -> int:
    """Process the chosen city and offer the main menu options."""
    user = update.effective_user
    context.user_data['city'] = update.message.text

    update.message.reply_text(f"Great! You chose {context.user_data['city']}.\n"
                              "Now, please choose an option from the main menu:",
                              reply_markup=main_menu_keyboard())

    return MAIN_MENU

def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Generate the main menu keyboard."""
    keyboard = [
        [InlineKeyboardButton("Schedule", callback_data="schedule"),
         InlineKeyboardButton("Something", callback_data="something")],
    ]
    return InlineKeyboardMarkup(keyboard)

def main_menu(update: Update, context: CallbackContext) -> int:
    """Handle main menu options."""
    query = update.callback_query
    if query is None:
        # Ignore None update (this can happen when the callback is triggered after conversation ends)
        return

    query.answer()

    if query.data == "schedule":
        url = "https://moscow.quizplease.ru/schedule" # only one choise yet
        schedule = extract_schedule(url)        
        context.user_data['schedule'] = schedule
        context.user_data['page'] = 0  # Initialize current page

        # query.message.reply_text("Here is the schedule for your chosen city:",
        #                          reply_markup=schedule_keyboard(context, context.user_data['page']))

        num_items_per_page = 5  # Number of items per page
        num_pages = math.ceil(len(schedule) / num_items_per_page)  # Calculate total number of pages

        current_page = context.user_data['page'] + 1  # Current page is 0-based, add 1 for user-friendly display

        message_text = f"Here is the schedule for your chosen city (Page {current_page}/{num_pages}):"
        query.message.reply_text(message_text, reply_markup=schedule_keyboard(context, context.user_data['page'], num_pages))

    elif query.data == "something":
        query.message.reply_text("You chose 'Something'.")

    return MAIN_MENU


def extract_schedule(url: str) -> list:
    # Implement your logic to extract schedule from the URL and return the list
    # Each item in the list should be a dictionary with 'date', 'title', 'package_number', 'time', and 'place' fields
    # For example:
    import json
    with open("schedule_example.json", "r") as json_file:
        schedule = json.load(json_file)
    return schedule

def schedule_keyboard(context: CallbackContext, current_page: int, num_pages: int) -> InlineKeyboardMarkup:
    """Generate the schedule keyboard with pagination."""
    schedule = context.user_data['schedule']
    items_per_page = 5  # Number of items per page
    start_index = current_page * items_per_page
    end_index = start_index + items_per_page
    current_schedule_page = schedule[start_index:end_index]

    buttons = [InlineKeyboardButton(f"{item['date']} - {item['title']}", callback_data=str(index))
               for index, item in enumerate(current_schedule_page, start=start_index)]

    if current_page > 0:
        buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"prev_{current_page - 1}_{num_pages}"))

    if end_index < len(schedule):
        buttons.append(InlineKeyboardButton("➡️ Next", callback_data=f"next_{current_page + 1}_{num_pages}"))

    keyboard = [buttons[i:i+2] for i in range(0, len(buttons), 2)]
    return InlineKeyboardMarkup(keyboard, resize_keyboard=True)

def button_callback(update: Update, context: CallbackContext) -> None:
    """Handle button clicks."""
    query = update.callback_query
    query.answer()

    if query.data.isdigit():
        item_index = int(query.data)
        schedule_item = context.user_data['schedule'][item_index]

        # response = f"Date: {schedule_item['date']}\nTitle: {schedule_item['title']}\n"
        # response += f"Package Number: {schedule_item['package_number']}\nTime: {schedule_item['time']}\nPlace: {schedule_item['place']}"
        response = f"Date: {schedule_item['date']}\nTime: {schedule_item['time']}\n"
        response += f"Package Number: {schedule_item['package_number']}\nPlace: {schedule_item['place']}"
        query.edit_message_text(response, reply_markup=schedule_keyboard(context, context.user_data['page'], num_pages))
    
        new_page = int(query.data)
        if new_page >= 0 and new_page < num_pages:
            context.user_data['page'] = new_page
            query.message.edit_text(
                f"Here is the schedule for your chosen city (Page {new_page + 1}/{num_pages}):",
                reply_markup=schedule_keyboard(context, new_page, num_pages)
            )

    elif query.data.startswith("prev_") or query.data.startswith("next_"):
        action, new_page, num_pages = query.data.split("_")  # Extract values from callback data
        new_page = int(new_page)
        num_pages = int(num_pages)
        
        if 0 <= new_page < num_pages:
            context.user_data['page'] = new_page
            query.message.edit_text(
                f"Here is the schedule for your chosen city (Page {new_page + 1}/{num_pages}):",
                reply_markup=schedule_keyboard(context, new_page, num_pages)
            )

    elif query.data == "schedule":
        # query.edit_message_text("You are already viewing the schedule.")
        num_pages = math.ceil(len(context.user_data['schedule']) / 5)  # Calculate total number of pages
        query.edit_message_text(
            f"Here is the schedule for your chosen city (Page 1/{num_pages}):",
            reply_markup=schedule_keyboard(context, 0, num_pages)
        )
    elif query.data == "something":
        query.edit_message_text("You chose 'Something'.")

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
