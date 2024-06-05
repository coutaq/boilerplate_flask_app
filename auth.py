import abc
from functools import wraps
import hashlib

from flask import Flask, jsonify, request
from db import DatabaseProvider, User
from kink import inject
from logger import ILogger
from utils import generate_token, jwt_decode


class IAuthServiceProvider(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def register_routes(self):
        raise NotImplementedError


@inject
class SimpleAuthServiceProvider(IAuthServiceProvider):
    def __init__(self, logger: ILogger, databaseProvider: DatabaseProvider, app: Flask) -> None:
        self.logger = logger
        self.app = app
        self.db = databaseProvider
        self.logger.info("AuthService started")

    def auth(self, func):
        @wraps(func)
        def decorated(*args, **kwargs):
            token = request.headers.get("Authorization")
            user = None
            if token:
                user = self.get_user_from_token(token)
                if not user:
                    jsonify(
                        {"error": "User not found or token doesn't match"}), 401
            return func(user, *args, **kwargs)

        return decorated

    def register_routes(self):
        auth = self

        def login_request():
            data = request.json
            if "login" not in data or "password" not in data:
                return jsonify({"message": "login and password are required"}), 400
            error, user = auth.login(data)
            if error:
                if error == 'credentials':
                    return jsonify({"message": "Invalid credentials"}), 401
                if error == 'pasword':
                    return jsonify({"errors": {"password": "invalid_password"}}), 401
            return jsonify({"token": user.token}), 200

        @auth.auth
        def get_user_info_request(user):
            if not user:
                return jsonify({"errors": {"error": "Unauthorized"}}), 401
            user_data = auth.db.schemas['user'].dump(user)
            return jsonify(user_data), 200

        def register_request():
            data = request.json
            if "email" not in data or "password" not in data:
                return jsonify({"message": "Email and password are required"}), 400
            user = auth.register(data)
            if not user:
                return jsonify({"message": "User already exists"}), 409
            return jsonify({"access_token": user.token}), 201

        self.app.add_url_rule(
            '/login', view_func=login_request, methods=["POST"])
        self.app.add_url_rule(
            '/me', view_func=get_user_info_request, methods=["GET"])
        self.app.add_url_rule(
            '/register', view_func=register_request, methods=["POST"])

        self.logger.debug("Simple Auth routes registred")

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

    def register_user(self, user_data: dict):
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


class TelegramAuthServiceProvider(IAuthServiceProvider):
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
