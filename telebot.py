import requests
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, Filters

# Replace 'YOUR_BOT_TOKEN' with the token you received from BotFather
BOT_TOKEN = '6521875912:AAGsFRaaEv3OMtb8apHfyayMFdPv6uT1foQ'

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Welcome to the Quiz Bot! Send /quiz to get a quiz question.")

def quiz(update: Update, context: CallbackContext):
    # Fetch data from the website and extract relevant information
    # Replace this with your actual scraping code
    quiz_question = "Sample question"
    options = ["Option A", "Option B", "Option C", "Option D"]

    response = f"Question: {quiz_question}\nOptions:\n"
    response += "\n".join(options)

    update.message.reply_text(response)

def main():
    # bot = Bot(BOT_TOKEN)
    # updater = Updater(bot=bot, use_context=True)
    updater = Updater(token=BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("quiz", quiz))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
