from functools import wraps
from flask import request, jsonify, g
from datetime import datetime, timedelta
import jwt

from utils.config import get_config

config = get_config()

# Temporary in-memory blacklist
# Later we can move this to database
TOKEN_BLACKLIST = set()


def generate_tokens(user_id, email):
    access_payload = {
        "user_id": user_id,
        "email": email,
        "type": "access",
        "exp": datetime.utcnow() + timedelta(
            minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    }

    refresh_payload = {
        "user_id": user_id,
        "email": email,
        "type": "refresh",
        "exp": datetime.utcnow() + timedelta(
            days=config.REFRESH_TOKEN_EXPIRE_DAYS
        )
    }

    access_token = jwt.encode(
        access_payload,
        config.JWT_SECRET_KEY,
        algorithm="HS256"
    )

    refresh_token = jwt.encode(
        refresh_payload,
        config.JWT_SECRET_KEY,
        algorithm="HS256"
    )

    return access_token, refresh_token


def decode_token(token, token_type=None):
    try:
        if token in TOKEN_BLACKLIST:
            return None

        payload = jwt.decode(
            token,
            config.JWT_SECRET_KEY,
            algorithms=["HS256"]
        )

        if token_type and payload.get("type") != token_type:
            return None

        return payload

    except jwt.ExpiredSignatureError:
        return None

    except jwt.InvalidTokenError:
        return None


def login_required_api(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({
                "error": "Authorization header missing"
            }), 401

        if not auth_header.startswith("Bearer "):
            return jsonify({
                "error": "Invalid authorization format"
            }), 401

        token = auth_header.split(" ")[1]

        payload = decode_token(token)

        if not payload:
            return jsonify({
                "error": "Invalid or expired token"
            }), 401

        g.user_id = payload["user_id"]
        g.user_email = payload["email"]

        return f(*args, **kwargs)

    return decorated