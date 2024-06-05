import abc
import hashlib
from db import DatabaseProvider, User
from kink import inject
from logger import ILogger
from utils import generate_token, jwt_decode


class IAuthServiceProvider(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_user_from_token(self, token: str):
        """Load in the data set"""
        raise NotImplementedError

    @abc.abstractmethod
    def register(self, user_data: dict):
        """Load in the data set"""
        raise NotImplementedError

    @abc.abstractmethod
    def login(self, login_data: dict):
        """Load in the data set"""
        raise NotImplementedError


@inject
class SimpleAuthServiceProvider(IAuthServiceProvider):
    def __init__(self, logger: ILogger, databaseProvider: DatabaseProvider) -> None:
        self.logger = logger
        self.db = databaseProvider
        self.logger.info("AuthService started")

    def get_user_from_token(self, token: str) -> User | bool:
        if token:
            try:
                token = token.split(" ")[1]
                if token:
                    payload = jwt_decode(token)
                    user_id = payload["user_id"]

                else:
                    user_id = None
            except:
                user_id = None
            try:
                user = (
                    User.select()
                    .where(User.id == user_id and User.token == token)
                    .first()
                )
                return user
            except User.DoesNotExist:
                pass
            return False

    def register(self, user_data: dict):
        email = user_data["email"]
        login = user_data["login"]
        password = user_data["password"]

        if User.select().where(User.email == email).exists():
            return False

        password_hash = hashlib.md5(password.encode()).hexdigest()
        new_user = User(email=email, password=password_hash, login=login)
        new_user.token = generate_token(new_user.id)
        new_user.save()
        return new_user

    def login(self, login_data: dict):
        login = login_data["login"]
        if "@" in login:
            user = User.get_or_none(User.email == login)
        else:
            user = User.get_or_none(User.login == login)
        password = login_data["password"]
        if not user:
            return 'credentials', None

        password_hash = hashlib.md5(password.encode()).hexdigest()
        if user.password != password_hash:
            return "password", None
        if not user.token:
            user.token = generate_token(user.id)
            user.save()
        return None, user


class TelegramAuthServiceProvider:
    pass
