import datetime
import re
import os
import jwt


def jwt_decode(token):
    jwt.decode(token, os.getenv("JWT_TOKEN"), algorithms=["HS256"])


def validate_email(email):
    return bool(re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email))


def validate_password(password):
    return bool(
        re.match(
            r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d!@#$%^&*()-_=+[\]{};:'\",<.>/?\\|]{8,}$",
            password,
        )
    )


def generate_token(user_id):
    token_payload = {
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=30),
    }
    token = jwt.encode(token_payload, os.getenv("JWT_TOKEN_SECRET"), algorithm="HS256")
    return token
