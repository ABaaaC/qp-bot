
# from schedule_parser import extract_schedule
BOT_TOKEN = '6521875912:AAGsFRaaEv3OMtb8apHfyayMFdPv6uT1foQ'
#!/usr/bin/env python

import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
import math

# Define the number of items per page
num_items_per_page = 5  # Number of items per page

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
        context.user_data['num_items_per_page'] = num_items_per_page

        current_page = context.user_data['page'] + 1  # Current page is 0-based, add 1 for user-friendly display
        num_pages = math.ceil(len(schedule) / num_items_per_page)  # Calculate total number of pages

        start_index = (current_page - 1) * num_items_per_page
        end_index = min(start_index + num_items_per_page, len(schedule))

        # schedule_text = "\n".join([f"{i + 1}. {item['title']} - {item['date']} at {item['time']}" for i, item in enumerate(schedule[start_index:end_index])])
        schedule_text = "\n".join([f"{i + 1 + start_index}. {item['title']} - {item['date']} at {item['time']}" for i, item in enumerate(schedule[start_index:end_index])])

        keyboard = []
        if end_index < len(schedule):
            keyboard.append(InlineKeyboardButton("➡️ Next", callback_data=f"next_{current_page + 1}_{num_pages}"))

        message_text = f"Here is the schedule for your chosen city (Page {current_page}/{num_pages}):\n{schedule_text}"
        query.message.edit_text(message_text, reply_markup=InlineKeyboardMarkup([keyboard]))

    elif query.data == "something":
        query.message.reply_text("You chose 'Something'.")

    return MAIN_MENU




def next_button_keyboard() -> InlineKeyboardMarkup:
    keyboard = [[InlineKeyboardButton("Next", callback_data="next")]]
    return InlineKeyboardMarkup(keyboard)





def extract_schedule(url: str) -> list:
    # Implement your logic to extract schedule from the URL and return the list
    # Each item in the list should be a dictionary with 'date', 'title', 'package_number', 'time', and 'place' fields
    # For example:
    import json
    with open("schedule_example.json", "r") as json_file:
        schedule = json.load(json_file)
    return schedule

def schedule_keyboard(context: CallbackContext, current_page: int, num_pages: int) -> InlineKeyboardMarkup:
    schedule = context.user_data.get('schedule', [])  # Get the schedule list from user data
    buttons = []
    start_index = (current_page - 1) * num_items_per_page
    end_index = min(start_index + num_items_per_page, len(schedule))

    for i in range(start_index, end_index):
        buttons.append(InlineKeyboardButton(f"{i + 1}. {schedule[i]['title']}", callback_data=str(i)))

    keyboard = [buttons[i:i+1] for i in range(0, len(buttons), 1)]

    if current_page > 0:
        buttons.insert(0, InlineKeyboardButton("⬅️ Previous", callback_data=f"prev_{current_page - 1}_{num_pages}"))
    if end_index < len(schedule):
        buttons.append(InlineKeyboardButton("➡️ Next", callback_data=f"next_{current_page + 1}_{num_pages}"))

    return InlineKeyboardMarkup(keyboard)




def button_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    num_items_per_page = context.user_data.get('num_items_per_page', 5)  # Get the value from user data

    if query.data.isdigit():
        item_index = int(query.data)
        schedule_item = context.user_data['schedule'][item_index]
        response = f"Date: {schedule_item['date']}\nTime: {schedule_item['time']}\n"
        response += f"Package Number: {schedule_item['package_number']}\nPlace: {schedule_item['place']}"
        query.edit_message_text(response, reply_markup=schedule_keyboard(context, context.user_data['page'], num_pages))
    
    elif query.data.startswith("prev_") or query.data.startswith("next_"):
        action, new_page, num_pages = query.data.split("_")  # Extract values from callback data
        new_page = int(new_page)
        num_pages = int(num_pages)

        if 0 <= new_page <= num_pages:
            context.user_data['page'] = new_page
            schedule = context.user_data.get('schedule', [])
            current_page = new_page
            start_index = (current_page - 1) * num_items_per_page
            end_index = min(start_index + num_items_per_page, len(schedule))

            # schedule_text = "\n".join([f"{i + 1}. {item['title']} - {item['date']} at {item['time']}" for i, item in enumerate(schedule[start_index:end_index])])
            # start_index = (current_page - 1) * num_items_per_page
            # end_index = min(start_index + num_items_per_page, len(schedule))

            # schedule_text = "\n".join([f"{i + 1}. {item['title']} - {item['date']} at {item['time']}" for i, item in enumerate(schedule[start_index:end_index])])
            schedule_text = "\n".join([f"{i + 1 + start_index}. {item['title']} - {item['date']} at {item['time']}" for i, item in enumerate(schedule[start_index:end_index])])

            keyboard = []
            if current_page > 1:
                keyboard.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"prev_{current_page - 1}_{num_pages}"))
            if end_index < len(schedule):
                keyboard.append(InlineKeyboardButton("➡️ Next", callback_data=f"next_{current_page + 1}_{num_pages}"))

            message_text = f"Here is the schedule for your chosen city (Page {current_page}/{num_pages}):\n{schedule_text}"
            query.message.edit_text(message_text, reply_markup=InlineKeyboardMarkup([keyboard]))


    elif query.data == "schedule":
        # query.edit_message_text("You are already viewing the schedule.")
        context.user_data['page'] = new_page
        current_page = new_page
        num_items_per_page = context.user_data.get('num_items_per_page', 5)
        num_pages = math.ceil(len(context.user_data['schedule']) / num_items_per_page)
        # query.edit_message_text(
        #     f"Here is the schedule for your chosen city (Page 1/{num_pages}):",
        #     reply_markup=schedule_keyboard(context, 0, num_pages)
        # )
        start_index = (current_page - 1) * num_items_per_page
        # start_index = new_page * num_items_per_page
        end_index = min(start_index + num_items_per_page, len(schedule))

        # schedule_text = "\n".join([f"{i + 1}. {item['title']} - {item['date']} at {item['time']}" for i, item in enumerate(schedule[start_index:end_index])])
        schedule_text = "\n".join([f"{i + 1 + start_index}. {item['title']} - {item['date']} at {item['time']}" for i, item in enumerate(schedule[start_index:end_index])])

        # schedule_text = "\n".join([f"{i + 1}. {item['title']} - {item['date']} at {item['time']}" for i, item in enumerate(schedule[start_index:end_index])])
        message_text = f"Here is the schedule for your chosen city (Page 1/{num_pages}):\n{schedule_text}"
        query.message.reply_text(
            message_text,
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
