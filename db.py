import abc
from peewee import *
import datetime
from logger import ILogger
from marshmallow import Schema, fields
from playhouse.shortcuts import ReconnectMixin
from kink import inject


class User(Model):
    id = AutoField()
    login = TextField()
    email = TextField()
    name = TextField()
    password = TextField()
    token = TextField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)


class UserSchema(Schema):
    email = fields.String()
    name = fields.String()
    login = fields.String()
    created_at = fields.DateTime()


@inject
class DatabaseProvider():
    def __init__(self, logger: ILogger, AppConfig) -> None:
        self.schemas = {}
        self.db = MySQLDatabase(AppConfig['DB_NAME'], host=AppConfig['DB_HOST'],
                                port=int(AppConfig['DB_PORT']), user=AppConfig['DB_USER'], password=AppConfig['DB_PASS'])
        self.db.bind([User])
        logger.info("Database initialized")
        self.schemas['user'] = UserSchema()
        self.schemas['users'] = UserSchema(many=True)


if __name__ == "__main__":
    from bootstrap import bootstrap_di
    from kink import di
    bootstrap_di()

    app_config = di['AppConfig']
    logger = di[ILogger]
    db = DatabaseProvider()
    tables = [db.User]
    db.db.drop_tables(tables)
    db.db.create_tables(tables)
    user_data = {
        "login": "admin",
        "email": "admin@admin.com",
        "name": "admin",
        "password": "1a1dc91c907325c69271ddf0c944bc72",
    }

    new_user = db.User.create(**user_data)
