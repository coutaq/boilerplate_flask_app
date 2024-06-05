from flask import Flask, request, jsonify
from auth import IAuthServiceProvider
from bootstrap import bootstrap_di
from logger import ILogger
from kink import di
from db import (
    DatabaseProvider,
)

bootstrap_di()
app_config = di['AppConfig']
app = di[Flask]
logger = di[ILogger]
db = di[DatabaseProvider]
authProvider = di[IAuthServiceProvider]


if __name__ == "__main__":
    logger.info("Starting debug server...")
    app.run(debug=True, port=app_config.get("APP_PORT"))
