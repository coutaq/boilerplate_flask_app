from threading import Thread
from kink import inject
import telebot

from logger import ILogger


@inject
class TelegramBot:
    thread = None

    def __init__(self, AppConfig, logger: ILogger) -> None:
        self.bot = telebot.TeleBot(
            AppConfig['TELEGRAM_TOKEN'])
        self.thread = Thread(target=self.listen, name="BotPollingThread")
        self.thread.start()
        logger.info("Telegram bot started")

    def listen(self):
        self.bot.infinity_polling()
        # pass

    def __del__(self):
        self.thread.stop()
