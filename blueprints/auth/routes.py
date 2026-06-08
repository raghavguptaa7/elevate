from flask import jsonify

from . import auth_bp

@auth_bp.route("/health")
def auth_health():
    return jsonify({
        "message": "Auth Blueprint Working"
    })