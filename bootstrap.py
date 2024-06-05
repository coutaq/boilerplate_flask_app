from http.client import HTTPException
import traceback
import uuid
from flask import Flask, jsonify
from flask_cors import CORS
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
    app = Flask(__name__)
    app.config["SECRET_KEY"] = uuid.uuid4().hex
    app.config["UPLOAD_FOLDER"] = app_config.get("APP_UPLOAD_FOLDER")
    cors = CORS(app)
    db = DatabaseProvider()
    auth_provider = SimpleAuthServiceProvider()
    di[Flask] = app
    di[DatabaseProvider] = db
    di[IAuthServiceProvider] = auth_provider
    di[TelegramBot] = TelegramBot()

    def app_exception_handler(e):
        code = 500
        if isinstance(e, HTTPException):
            code = e.code
        logger.error(traceback.format_exc())
        return jsonify(error=f"Error: {str(e)}!"), code

    app.register_error_handler(Exception, app_exception_handler)

    if DatabaseProvider in di:
        db.register_hooks()
    auth_provider.register_routes()
