from flask import jsonify, g
from . import dashboard_bp
from middleware.auth import login_required_api
from utils.db_utils import query_db


@dashboard_bp.route("/", methods=["GET"])
@login_required_api
def dashboard():

    user_id = g.user_id

    total_resumes = query_db(
        "SELECT COUNT(*) as count FROM resumes WHERE user_id=?",
        (user_id,),
        one=True
    )["count"]

    total_interviews = query_db(
        "SELECT COUNT(*) as count FROM interviews WHERE user_id=?",
        (user_id,),
        one=True
    )["count"]

    total_quizzes = query_db(
        "SELECT COUNT(*) as count FROM quizzes WHERE user_id=?",
        (user_id,),
        one=True
    )["count"]

    avg_score = query_db(
        "SELECT AVG(score) as avg_score FROM quizzes WHERE user_id=?",
        (user_id,),
        one=True
    )

    return jsonify({
        "total_resumes": total_resumes,
        "total_interviews": total_interviews,
        "total_quizzes": total_quizzes,
        "average_quiz_score": avg_score["avg_score"] or 0
    })