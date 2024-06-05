from functools import wraps
import hashlib
import os
import uuid
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from auth import IAuthServiceProvider
from bootstrap import bootstrap_di
from logger import ILogger
from utils import generate_token, jwt_decode
from kink import di, inject
from db import (
    DatabaseProvider,
)
from flask_cors import CORS

bootstrap_di()

app_config = di['AppConfig']
logger = di[ILogger]
db = di[DatabaseProvider]
authProvider = di[IAuthServiceProvider]
app = Flask(__name__)
app.config["SECRET_KEY"] = uuid.uuid4().hex
app.config["UPLOAD_FOLDER"] = app_config.get("APP_UPLOAD_FOLDER")
cors = CORS(app)


@app.before_request
def _db_connect():
    db.db.connect()


@app.teardown_request
def _db_close(exc):
    if not db.db.is_closed():
        db.db.close()


def auth(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        user = None
        if token:
            user = authProvider.get_user_from_token(token)
            if not user:
                jsonify({"error": "User not found or token doesn't match"}), 401
        return func(user, *args, **kwargs)

    return decorated


@app.route("/me", methods=["GET"])
@auth
def get_user_info(user):
    if not user:
        return jsonify({"errors": {"error": "Unauthorized"}}), 401
    user_data = db.schemas['user'].dump(user)
    return jsonify(user_data), 200


@app.route("/register", methods=["POST"])
def register():
    data = request.json
    if "email" not in data or "password" not in data:
        return jsonify({"message": "Email and password are required"}), 400

    user = authProvider.register(data)
    if not user:
        return jsonify({"message": "User already exists"}), 409
    return jsonify({"access_token": user.token}), 201


# Login route
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    if "login" not in data or "password" not in data:
        return jsonify({"message": "login and password are required"}), 400
    error, user = authProvider.login(data)
    if error:
        if error == 'credentials':
            return jsonify({"message": "Invalid credentials"}), 401
        if error == 'pasword':
            return jsonify({"errors": {"password": "invalid_password"}}), 401
    return jsonify({"token": user.token}), 200


@app.route("/users", methods=["GET"])
def get_users():
    users = db.User.select()
    result = db.schemas['users'].dump(users)
    return jsonify(result)


@auth
@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"message": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"message": "No selected file"}), 400

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app_config.get("UPLOAD_FOLDER"), filename)
        file.save(file_path)
        return (
            jsonify({"message": "File uploaded successfully",
                    "filename": filename}),
            201,
        )

    return jsonify({"message": "File upload failed"}), 500


if __name__ == "__main__":
    # pass
    logger.info("Starting debug server...")
    app.run(debug=True, port=app_config.get("APP_PORT"))
