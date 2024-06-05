from auth import IAuthServiceProvider, SimpleAuthServiceProvider
from db import DatabaseProvider
from kink import di
from dotenv import dotenv_values

from logger import ILogger, create_logger
from telegram import TelegramBot


def bootstrap_di() -> None:
    app_config = dotenv_values(".env")
    logger = create_logger(app_config)
    logger.info("Bootstrapping application")
    di["AppConfig"] = app_config
    di[ILogger] = logger
    di[DatabaseProvider] = DatabaseProvider()
    di[IAuthServiceProvider] = SimpleAuthServiceProvider()
    di[TelegramBot] = TelegramBot()
