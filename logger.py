import abc
from zenlog import log as zenlog
from datetime import datetime

default_logger = 'CONSOLE'
default_log_level = "INFO"

log_levels = {
    "DEBUG": 0,
    "INFO": 1,
    "WARNING": 2,
    "ERROR": 3,
    "CRITICAL": 4
}


def format_text_with_timestamp(text: str) -> str:
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    return f"{dt_string}: {text}"


class ILogger(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self, log_level: str) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def debug(self, text: str):
        raise NotImplementedError

    @abc.abstractmethod
    def info(self, text: str):
        raise NotImplementedError

    @abc.abstractmethod
    def warning(self, text: str):
        raise NotImplementedError

    @abc.abstractmethod
    def error(self, text: str):
        raise NotImplementedError

    @abc.abstractmethod
    def critical(self, text: str):
        raise NotImplementedError


class ConsoleLogger(ILogger):
    def __init__(self, log_level: str) -> None:
        self.log_level = log_level

    def debug(self, text: str):
        if log_levels[self.log_level] <= log_levels["DEBUG"]:
            zenlog.debug(format_text_with_timestamp(text))

    def info(self, text: str):
        if log_levels[self.log_level] <= log_levels["INFO"]:
            zenlog.info(format_text_with_timestamp(text))

    def warning(self, text: str):
        if log_levels[self.log_level] <= log_levels["WARNING"]:
            zenlog.warning(format_text_with_timestamp(text))

    def error(self, text: str):
        if log_levels[self.log_level] <= log_levels["ERROR"]:
            zenlog.error(format_text_with_timestamp(text))

    def critical(self, text: str):
        if log_levels[self.log_level] <= log_levels["CRITICAL"]:
            zenlog.critical(format_text_with_timestamp(text))


loggers = {
    "CONSOLE": ConsoleLogger
}


def create_logger(conf: dict):
    logger = loggers.get(conf.get("LOGGER_TYPE", default_logger))(
        log_level=conf.get("LOG_LEVEL", default_log_level))

    return logger
