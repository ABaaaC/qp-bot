
from .schedule_parser import extract_schedule
BOT_TOKEN = '6521875912:AAGsFRaaEv3OMtb8apHfyayMFdPv6uT1foQ'

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

# Replace 'YOUR_BOT_TOKEN' with the token you received from BotFather

# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    reply_with_suggestions(update, rf"Hi {user.mention_html()}! This is your quiz bot.")
    
# def start(update: Update, context: CallbackContext) -> None:
#     """Send a message when the command /start is issued.
#     OLD"""
#     user = update.effective_user
#     update.message.reply_html(
#         rf"Hi {user.mention_html()}! This is your quiz bot. Send /quiz to get a quiz question.",
#     )

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    reply_with_suggestions(update, "This bot provides quiz information.")

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

# ... (previous code)

def handle_text(update: Update, context: CallbackContext) -> None:
    """Handle text messages and suggest using /quiz and /help commands."""
    user_text = update.message.text.lower()

    if "/quiz" in user_text:
        update.message.reply_text("Send /quiz to get a quiz question.")
    elif "/help" in user_text:
        update.message.reply_text("Send /help to learn how to use this bot.")
    else:
        # Create a custom keyboard with possible commands
        custom_keyboard = [
            ["/quiz", "/help"],
        ]
        reply_markup = ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)

        update.message.reply_text(
            "I'm a quiz bot! You can use these commands:",
            reply_markup=reply_markup,
        )

# ... (rest of the code)

def handle_suggestion(update: Update, context: CallbackContext) -> None:
    """Handle suggestions when user starts typing '/'. Show possible commands."""
    user_text = update.message.text.lower()

    if user_text.startswith("/"):
        # Create a custom keyboard with possible commands
        custom_keyboard = [
            ["/quiz", "/help"],
        ]
        reply_markup = ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)

        update.message.reply_text(
            "You can use these commands:",
            reply_markup=reply_markup,
        )

def reply_with_suggestions(update: Update, text: str) -> None:
    """Reply to the user's message with suggestions and the provided text."""
    custom_keyboard = [
        ["/quiz", "/help"],
    ]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)

    # update.message.reply_text(
    #     text,
    #     reply_markup=reply_markup,
    # )
    update.message.reply_html(
        text,
        reply_markup=reply_markup,
    )

def main() -> None:
    """Start the bot."""
    updater = Updater(token=BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("quiz", quiz))
    dispatcher.add_handler(MessageHandler(Filters.text & Filters.command, handle_text))  # Handle text commands
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_suggestion))  # Handle suggestions

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
