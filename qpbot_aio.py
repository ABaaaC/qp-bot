
from dotenv import dotenv_values
config = dotenv_values(".env")
BOT_TOKEN = config.get("BOT_TOKEN")
BASE_WEBHOOK_URL = config.get("BASE_WEBHOOK_URL")
WEBHOOK_PATH = config.get("WEBHOOK_PATH")

# bind localhost only to prevent any external access
WEB_SERVER_HOST = config.get("WEB_SERVER_HOST")
# Port for incoming request from reverse proxy. Should be any available port
WEB_SERVER_PORT = config.get("WEB_SERVER_PORT")
#!/usr/bin/env python

import logging

from aiogram import Bot, Dispatcher, Router
from aiogram.enums import ParseMode


from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

# Define the number of items per page

form_router = Router()

# Enable logging
fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
clrd_fmt = '\x1b[38;5;226m' + fmt + '\x1b[0m'
logging.basicConfig(format=fmt, level=logging.INFO, )
logger = logging.getLogger(__name__)


async def on_startup(bot: Bot) -> None:
    # If you have a self-signed SSL certificate, then you will need to send a public
    # certificate to Telegram
    await bot.set_webhook(f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}/{BOT_TOKEN}")

"""Start the bot."""
dp = Dispatcher()
dp.include_router(form_router)

# Register startup hook to initialize webhook
dp.startup.register(on_startup)

# Initialize Bot instance with a default parse mode which will be passed to all API calls
bot = Bot(BOT_TOKEN, parse_mode=ParseMode.HTML)

# Create aiohttp.web.Application instance
app = web.Application()

# Create an instance of request handler,
# aiogram has few implementations for different cases of usage
# In this example we use SimpleRequestHandler which is designed to handle simple cases
webhook_requests_handler = SimpleRequestHandler(
    dispatcher=dp,
    bot=bot,
    # secret_token=WEBHOOK_SECRET,
)
# Register webhook handler on application
webhook_requests_handler.register(app, path=f"{WEBHOOK_PATH}/{BOT_TOKEN}")

# Mount dispatcher startup and shutdown hooks to aiohttp application
setup_application(app, dp, bot=bot)

    
if __name__ == "__main__":
    # And finally start webserver
    web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)
