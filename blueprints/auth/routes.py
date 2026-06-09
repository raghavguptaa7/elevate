from flask import request, jsonify, g
import sqlite3

from . import auth_bp
from utils.password_utils import hash_password, verify_password
from middleware.auth import (
    generate_tokens,
    login_required_api,
    decode_token,
    TOKEN_BLACKLIST
)


@auth_bp.route("/health")
def auth_health():
    return jsonify({
        "message": "Auth Blueprint Working"
    })


@auth_bp.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "error": "Email and password required"
        }), 400

    conn = sqlite3.connect("database/database.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM users WHERE email=?",
        (email,)
    )

    existing = cursor.fetchone()

    if existing:
        conn.close()
        return jsonify({
            "error": "Email already exists"
        }), 400

    hashed_password = hash_password(password)

    cursor.execute(
        "INSERT INTO users(email,password) VALUES (?,?)",
        (email, hashed_password)
    )

    user_id = cursor.lastrowid

    conn.commit()
    conn.close()

    access_token, refresh_token = generate_tokens(
        user_id,
        email
    )

    return jsonify({
        "message": "User created",
        "access_token": access_token,
        "refresh_token": refresh_token
    })


@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    conn = sqlite3.connect("database/database.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE email=?",
        (email,)
    )

    user = cursor.fetchone()

    conn.close()

    if not user:
        return jsonify({
            "error": "Invalid credentials"
        }), 401

    if not verify_password(password, user[2]):
        return jsonify({
            "error": "Invalid credentials"
        }), 401

    access_token, refresh_token = generate_tokens(
        user[0],
        user[1]
    )

    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "refresh_token": refresh_token
    })


@auth_bp.route("/me", methods=["GET"])
def me():

    return jsonify({
        "user_id": g.user_id,
        "email": g.user_email
    })
@auth_bp.route("/refresh", methods=["POST"])
def refresh():

    data = request.get_json()

    refresh_token = data.get("refresh_token")

    if not refresh_token:
        return jsonify({
            "error": "Refresh token required"
        }), 400

    payload = decode_token(
        refresh_token,
        token_type="refresh"
    )

    if not payload:
        return jsonify({
            "error": "Invalid refresh token"
        }), 401

    access_token, new_refresh_token = generate_tokens(
        payload["user_id"],
        payload["email"]
    )

    return jsonify({
        "access_token": access_token,
        "refresh_token": new_refresh_token
    })    
@auth_bp.route("/logout", methods=["POST"])
def logout():

    auth_header = request.headers.get("Authorization")

    token = auth_header.split(" ")[1]

    TOKEN_BLACKLIST.add(token)

    return jsonify({
        "message": "Logged out successfully"
    })    