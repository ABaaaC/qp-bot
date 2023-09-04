from src.telebot8 import main
import logging

clrd_fmt = '\x1b[38;5;226m' + '%(levelname)s' + ': %(name)s - (%(asctime)s)' + ' \t\x1b[0m %(message)s'
logging.basicConfig(level=logging.INFO, format=clrd_fmt)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    main()