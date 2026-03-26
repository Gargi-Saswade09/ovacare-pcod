from flask import Blueprint, request, jsonify
from database.db import get_db_connection

user_bp = Blueprint("user", __name__)


# Get User Profile
@user_bp.route("/user/<int:user_id>", methods=["GET"])
def get_user(user_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT id, email, created_at FROM users WHERE id=%s"
    cursor.execute(query, (user_id,))

    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user:
        return jsonify(user)
    else:
        return jsonify({"message": "User not found"}), 404


# Get User Reports (Dashboard History)
@user_bp.route("/reports/<int:user_id>", methods=["GET"])
def get_user_reports(user_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    SELECT id, risk_level, risk_score, bmi, created_at
    FROM reports
    WHERE user_id = %s
    ORDER BY created_at DESC
    """

    cursor.execute(query, (user_id,))
    reports = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(reports)


# Delete a Report
@user_bp.route("/delete-report/<int:report_id>", methods=["DELETE"])
def delete_report(report_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    query = "DELETE FROM reports WHERE id=%s"
    cursor.execute(query, (report_id,))

    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"message": "Report deleted successfully"})


# Update User Email
@user_bp.route("/update-user/<int:user_id>", methods=["PUT"])
def update_user(user_id):

    data = request.json
    new_email = data["email"]

    conn = get_db_connection()
    cursor = conn.cursor()

    query = "UPDATE users SET email=%s WHERE id=%s"
    cursor.execute(query, (new_email, user_id))

    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"message": "User updated successfully"})