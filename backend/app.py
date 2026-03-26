import os
import json
import joblib
import random
import pandas as pd

import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

from datetime import datetime, timedelta
from urllib.parse import quote

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, Response
import pdfkit

pdfkit_config = pdfkit.configuration(
    wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
)
from werkzeug.security import generate_password_hash, check_password_hash

from database.db import get_db_connection
from config import SECRET_KEY
from chatbot.chat_service import get_chatbot_service
from services.email_service import (
    send_otp_email,
    send_reminder_email,
    send_contact_email_to_admin,
    send_contact_ack_email
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.abspath(os.path.join(BASE_DIR, "../frontend/src/pages"))
STATIC_DIR = os.path.abspath(os.path.join(BASE_DIR, "../frontend/src"))
MODEL_PATH = os.path.join(BASE_DIR, "model", "best_pcod_model.pkl")
FEATURES_PATH = os.path.join(BASE_DIR, "model", "model_features.pkl")

app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR,
    static_folder=STATIC_DIR,
    static_url_path="/static"
)

app.secret_key = SECRET_KEY
pcod_model = joblib.load(MODEL_PATH)

if os.path.exists(FEATURES_PATH):
    model_features = joblib.load(FEATURES_PATH)
else:
    model_features = [
        "age",
        "bmi",
        "cycle_regular",
        "cycle_length_days",
        "weight_gain",
        "hair_growth",
        "skin_darkening",
        "hair_loss",
        "acne",
        "fast_food",
        "exercise"
    ]


# ---------------------------
# BASIC HELPERS
# ---------------------------
def is_logged_in():
    return "user_id" in session


def calculate_bmi(height_cm, weight_kg):
    height_m = float(height_cm) / 100
    bmi = float(weight_kg) / (height_m * height_m)

    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25:
        category = "Normal"
    elif bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"

    return round(bmi, 2), category


def get_user_by_email(email):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, email, password, is_verified FROM users WHERE email = %s", (email,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


def get_user_by_id(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, email, password, is_verified FROM users WHERE id = %s", (user_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


def get_profile(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, user_id, age, phone, city, occupation, height_cm, weight_kg,
               menstrual_cycle_length, period_duration, last_period_date, cycle_regular, notes
        FROM user_profiles
        WHERE user_id = %s
    """, (user_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


def get_latest_pcod_test(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, predicted_risk, probability, created_at, stress_level, stress_adjustment
        FROM pcod_tests
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT 1
    """, (user_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


def get_latest_stress_result_row(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, stress_score, stress_level, created_at, answers_json
        FROM stress_quiz_results
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT 1
    """, (user_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


def get_latest_bmi_record(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, height_cm, weight_kg, bmi_value, bmi_category, created_at
        FROM bmi_records
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT 1
    """, (user_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


def create_notification(user_id, title, message, notif_type="info"):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()

    if user:
        cur.execute("""
            INSERT INTO notifications (user_id, title, message, type)
            VALUES (%s, %s, %s, %s)
        """, (user_id, title, message, notif_type))
        conn.commit()

    cur.close()
    conn.close()


def get_notifications(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, title, message, type, is_read, created_at
        FROM notifications
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT 10
    """, (user_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def mark_all_notifications_read(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE notifications SET is_read = TRUE WHERE user_id = %s", (user_id,))
    conn.commit()
    cur.close()
    conn.close()


def weekly_stress_due(user_id):
    latest = get_latest_stress_result_row(user_id)
    if not latest:
        return True
    return datetime.now() - latest[3] >= timedelta(days=7)


def monthly_pcod_due(user_id):
    latest = get_latest_pcod_test(user_id)
    if not latest:
        return True
    return datetime.now() - latest[3] >= timedelta(days=30)


def notification_exists_recently(user_id, title, within_days):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id
        FROM notifications
        WHERE user_id = %s
          AND title = %s
          AND created_at >= NOW() - (%s * INTERVAL '1 day')
        LIMIT 1
    """, (user_id, title, within_days))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row is not None


def ensure_due_notifications(user_id):
    user = get_user_by_id(user_id)
    if not user:
        return

    user_name = user[1]
    user_email = user[2]

    if weekly_stress_due(user_id) and not notification_exists_recently(user_id, "Weekly Stress Quiz Due", 7):
        title = "Weekly Stress Quiz Due"
        message = "Your weekly stress quiz is due. Please complete it for personalized recommendations."
        create_notification(user_id, title, message, "warning")
        send_reminder_email(user_email, user_name, title, message)

    if monthly_pcod_due(user_id) and not notification_exists_recently(user_id, "Monthly PCOD Test Due", 30):
        title = "Monthly PCOD Test Due"
        message = "Your monthly PCOD test is due. Please complete it to update your dashboard and plans."
        create_notification(user_id, title, message, "warning")
        send_reminder_email(user_email, user_name, title, message)


def get_stress_questions():
    return [
        "How often have you been upset because of something that happened unexpectedly?",
        "How often have you felt that you were unable to control important things in your life?",
        "How often have you felt nervous and stressed?",
        "How often have you felt confident about your ability to handle your personal problems?",
        "How often have you felt that things were going your way?",
        "How often have you found that you could not cope with all the things you had to do?",
        "How often have you been able to control irritations in your life?",
        "How often have you felt that you were on top of things?",
        "How often have you been angered because of things that were outside of your control?",
        "How often have you felt that difficulties were piling up so high that you could not overcome them?"
    ]


def calculate_pss_score(responses):
    reverse_indices = [3, 4, 6, 7]
    total_score = 0

    for i, score in enumerate(responses):
        if i in reverse_indices:
            score = 4 - score
        total_score += score

    return total_score


def calculate_stress_level(score):
    if score <= 13:
        return "Low"
    elif score <= 26:
        return "Moderate"
    else:
        return "High"


def stress_adjustment_value(stress_level):
    if stress_level == "High":
        return 8.0
    elif stress_level == "Moderate":
        return 4.0
    return 0.0


def adjust_probability_with_stress(base_probability, stress_level):
    adjusted = min(base_probability + stress_adjustment_value(stress_level), 99.0)
    return round(adjusted, 2)


def risk_from_probability(probability):
    if probability >= 65:
        return "High Risk of PCOD"
    elif probability >= 40:
        return "Moderate Risk of PCOD"
    return "Low Risk of PCOD"


def stress_level_to_score(stress_level):
    if stress_level == "High":
        return 80
    elif stress_level == "Moderate":
        return 50
    return 20


def generate_diet_plan(pcod_result=None, stress_result=None):
    if pcod_result and stress_result:
        if pcod_result == "High Risk of PCOD" and stress_result == "High":
            return [
                "Eat high-fiber foods like oats, vegetables, fruits, and pulses.",
                "Include protein in every meal such as dal, eggs, paneer, tofu, or sprouts.",
                "Reduce sugar, bakery foods, packaged snacks, and soft drinks.",
                "Add calming foods like curd, nuts, seeds, banana, and herbal tea.",
                "Avoid skipping meals and drink enough water."
            ]
        if pcod_result in ["High Risk of PCOD", "Moderate Risk of PCOD"]:
            return [
                "Follow a low-glycemic balanced diet.",
                "Increase vegetables, fiber, and protein intake.",
                "Limit fast food, sugary foods, and refined flour."
            ]
        return [
            "Maintain balanced home-cooked meals.",
            "Include fruits, vegetables, and good hydration.",
            "Add stress-supportive foods like seeds and curd."
        ]

    if pcod_result and not stress_result:
        if pcod_result in ["High Risk of PCOD", "Moderate Risk of PCOD"]:
            return [
                "Focus on hormone-friendly meals with high fiber and protein.",
                "Avoid deep-fried and high-sugar foods.",
                "Eat at regular timings and stay hydrated."
            ]
        return [
            "Maintain a healthy balanced diet.",
            "Continue regular meal timing and hydration."
        ]

    if stress_result and not pcod_result:
        if stress_result == "High":
            return [
                "Eat simple balanced meals on time.",
                "Avoid too much caffeine and junk food.",
                "Include curd, banana, seeds, nuts, and enough water."
            ]
        return [
            "Maintain balanced regular meals.",
            "Include vegetables, fruits, and proteins."
        ]

    return [
        "General recommendation: balanced meals, less junk food, enough water, regular meal timing.",
        "Complete the stress quiz and PCOD test for personalized recommendations."
    ]


def generate_exercise_plan(pcod_result=None, stress_result=None):
    if pcod_result and stress_result:
        if pcod_result == "High Risk of PCOD" and stress_result == "High":
            return [
                "20 to 30 minutes brisk walking daily.",
                "10 minutes breathing exercises.",
                "Gentle yoga for hormonal balance.",
                "Avoid overtraining and focus on consistency."
            ]
        if pcod_result in ["High Risk of PCOD", "Moderate Risk of PCOD"]:
            return [
                "30 minutes walk or cycling 5 days a week.",
                "Light strength training 2 to 3 times weekly.",
                "Add stretching or yoga."
            ]
        return [
            "Regular walking, yoga, stretching, and light cardio."
        ]

    if pcod_result and not stress_result:
        if pcod_result in ["High Risk of PCOD", "Moderate Risk of PCOD"]:
            return [
                "Brisk walking, cycling, yoga, and beginner strength workouts."
            ]
        return [
            "30 minutes regular movement daily."
        ]

    if stress_result and not pcod_result:
        if stress_result == "High":
            return [
                "Daily walking, deep breathing, light yoga, and evening stretching."
            ]
        return [
            "Regular walking and mobility exercises."
        ]

    return [
        "General recommendation: 30 minutes movement daily, stretching, and walking.",
        "Complete the stress quiz and PCOD test for personalized recommendations."
    ]


def get_user_health_context(user_id):
    latest_pcod = get_latest_pcod_test(user_id)
    latest_stress = get_latest_stress_result_row(user_id)

    risk = latest_pcod[1] if latest_pcod else "Unknown"
    probability = float(latest_pcod[2]) if latest_pcod and latest_pcod[2] is not None else None
    stress_level = latest_stress[2] if latest_stress else "Unknown"
    stress_score = int(latest_stress[1]) if latest_stress and latest_stress[1] is not None else None

    return {
        "risk": risk,
        "probability": probability,
        "stress_level": stress_level,
        "stress_score": stress_score
    }


# ---------------------------
# OTP / MAIL
# ---------------------------
def send_email_otp(receiver_email, otp_code, purpose):
    return send_otp_email(receiver_email, otp_code, purpose)


def create_otp(email, purpose):
    otp = str(random.randint(100000, 999999))
    expires_at = datetime.now() + timedelta(minutes=10)

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO otp_codes (email, otp_code, purpose, expires_at, is_used)
        VALUES (%s, %s, %s, %s, FALSE)
    """, (email, otp, purpose, expires_at))
    conn.commit()
    cur.close()
    conn.close()

    return otp


def verify_otp(email, otp, purpose):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, expires_at
        FROM otp_codes
        WHERE email = %s AND otp_code = %s AND purpose = %s AND is_used = FALSE
        ORDER BY created_at DESC
        LIMIT 1
    """, (email, otp, purpose))
    row = cur.fetchone()

    if not row:
        cur.close()
        conn.close()
        return False

    otp_id, expires_at = row

    if datetime.now() > expires_at:
        cur.close()
        conn.close()
        return False

    cur.execute("UPDATE otp_codes SET is_used = TRUE WHERE id = %s", (otp_id,))
    conn.commit()
    cur.close()
    conn.close()
    return True


# ---------------------------
# CALENDAR
# ---------------------------
def google_calendar_link(title, details, start_dt, end_dt):
    def fmt(dt):
        return dt.strftime("%Y%m%dT%H%M%S")

    return (
        "https://calendar.google.com/calendar/render?action=TEMPLATE"
        f"&text={quote(title)}"
        f"&details={quote(details)}"
        f"&dates={fmt(start_dt)}/{fmt(end_dt)}"
    )


def next_weekly_stress_link():
    start_dt = datetime.now() + timedelta(days=7)
    end_dt = start_dt + timedelta(minutes=20)
    return google_calendar_link(
        "Weekly Stress Quiz - OvaCare",
        "Complete your weekly stress quiz on OvaCare.",
        start_dt,
        end_dt
    )


def next_monthly_pcod_link():
    start_dt = datetime.now() + timedelta(days=30)
    end_dt = start_dt + timedelta(minutes=30)
    return google_calendar_link(
        "Monthly PCOD Test - OvaCare",
        "Complete your monthly PCOD self-assessment on OvaCare.",
        start_dt,
        end_dt
    )


def get_unread_notification_count(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*) FROM notifications
        WHERE user_id = %s AND is_read = FALSE
    """, (user_id,))
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return count


@app.route("/download_stress_quiz_ics")
def download_stress_quiz_ics():
    if not is_logged_in():
        return redirect(url_for("login"))

    start_dt = datetime.now() + timedelta(days=7)
    end_dt = start_dt + timedelta(minutes=20)

    content = f"""BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
SUMMARY:Weekly Stress Quiz - OvaCare
DESCRIPTION:Complete your weekly stress quiz on OvaCare.
DTSTART:{start_dt.strftime("%Y%m%dT%H%M%S")}
DTEND:{end_dt.strftime("%Y%m%dT%H%M%S")}
END:VEVENT
END:VCALENDAR
"""
    return Response(
        content,
        mimetype="text/calendar",
        headers={"Content-Disposition": "attachment; filename=weekly_stress_quiz.ics"}
    )


@app.route("/download_pcod_test_ics")
def download_pcod_test_ics():
    if not is_logged_in():
        return redirect(url_for("login"))

    start_dt = datetime.now() + timedelta(days=30)
    end_dt = start_dt + timedelta(minutes=30)

    content = f"""BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
SUMMARY:Monthly PCOD Test - OvaCare
DESCRIPTION:Complete your monthly PCOD test on OvaCare.
DTSTART:{start_dt.strftime("%Y%m%dT%H%M%S")}
DTEND:{end_dt.strftime("%Y%m%dT%H%M%S")}
END:VEVENT
END:VCALENDAR
"""
    return Response(
        content,
        mimetype="text/calendar",
        headers={"Content-Disposition": "attachment; filename=monthly_pcod_test.ics"}
    )


# ---------------------------
# FLOW HELPERS
# ---------------------------
def require_login():
    if not is_logged_in():
        flash("Please login first.")
        return False

    current_user = get_user_by_id(session["user_id"])
    if not current_user:
        session.clear()
        flash("Session expired. Please login again.")
        return False

    return True


def require_stress_before_bmi():
    latest = get_latest_stress_result_row(session["user_id"])
    return latest is not None


def require_bmi_before_pcod():
    latest = get_latest_bmi_record(session["user_id"])
    return latest is not None


# ---------------------------
# ROUTES
# ---------------------------
@app.route("/")
def home():
    if is_logged_in():
        current_user = get_user_by_id(session["user_id"])
        if not current_user:
            session.clear()
            flash("Your session expired after database reset. Please login again.")
            return redirect(url_for("login"))

        session["user_name"] = current_user[1]
        session["user_email"] = current_user[2]

        ensure_due_notifications(session["user_id"])

        profile = get_profile(session["user_id"])
        latest_stress = get_latest_stress_result_row(session["user_id"])
        latest_pcod = get_latest_pcod_test(session["user_id"])
        latest_bmi = get_latest_bmi_record(session["user_id"])
        notifications = get_notifications(session["user_id"])
        unread_count = get_unread_notification_count(session["user_id"])

        return render_template(
            "index.html",
            profile=profile,
            latest_stress=latest_stress,
            latest_pcod=latest_pcod,
            latest_bmi=latest_bmi,
            notifications=notifications,
            unread_count=unread_count,
            stress_due=weekly_stress_due(session["user_id"]),
            pcod_due=monthly_pcod_due(session["user_id"]),
            stress_calendar_link=next_weekly_stress_link(),
            pcod_calendar_link=next_monthly_pcod_link()
        )

    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if is_logged_in():
        current_user = get_user_by_id(session["user_id"])
        if current_user:
            return redirect(url_for("home"))
        session.clear()

    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        user = get_user_by_email(email)

        if user and user[4] and check_password_hash(user[3], password):
            session["user_id"] = user[0]
            session["user_name"] = user[1]
            session["user_email"] = user[2]
            ensure_due_notifications(user[0])
            flash(f"Welcome back, {user[1]}!")
            return redirect(url_for("home"))

        flash("Invalid email or password, or account not verified.")

    return render_template("Login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if is_logged_in():
        current_user = get_user_by_id(session["user_id"])
        if current_user:
            return redirect(url_for("home"))
        session.clear()

    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        import re

        if len(password) < 6:
            flash("Password must be at least 6 characters long.")
            return redirect(url_for("register"))

        if not re.search(r"[A-Z]", password):
            flash("Password must contain at least one uppercase letter.")
            return redirect(url_for("register"))

        if not re.search(r"[a-z]", password):
            flash("Password must contain at least one lowercase letter.")
            return redirect(url_for("register"))

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            flash("Password must contain at least one special character.")
            return redirect(url_for("register"))

        existing_user = get_user_by_email(email)
        if existing_user:
            flash("Email already registered")
            return redirect(url_for("register"))

        session["pending_register"] = {
            "name": name,
            "email": email,
            "password": generate_password_hash(password)
        }

        otp = create_otp(email, "register")
        sent = send_email_otp(email, otp, "register")

        if sent:
            flash("OTP sent to your email.")
            return redirect(url_for("verify_register"))
        else:
            flash("Unable to send OTP email. Check sender email and app password.")
            return redirect(url_for("register"))

    return render_template("register.html")


@app.route("/verify_register", methods=["GET", "POST"])
def verify_register():
    pending = session.get("pending_register")
    if not pending:
        flash("Registration session expired. Please register again.")
        return redirect(url_for("register"))

    if request.method == "POST":
        otp = request.form["otp"].strip()

        if verify_otp(pending["email"], otp, "register"):
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO users (name, email, password, is_verified)
                VALUES (%s, %s, %s, TRUE)
                RETURNING id
            """, (pending["name"], pending["email"], pending["password"]))
            user_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            conn.close()

            session.pop("pending_register", None)
            session["user_id"] = user_id
            session["user_name"] = pending["name"]
            session["user_email"] = pending["email"]

            flash("Registration successful.")
            return redirect(url_for("home"))

        flash("Invalid or expired OTP.")

    return render_template("verify_register.html")


@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        try:
            email = request.form.get("email", "").strip().lower()

            if not email:
                flash("Please enter your email address.")
                return redirect(url_for("forgot_password"))

            user = get_user_by_email(email)

            if not user:
                flash("Email not found.")
                return redirect(url_for("forgot_password"))

            otp = create_otp(email, "reset")
            sent = send_email_otp(email, otp, "reset")

            if sent:
                session["reset_email"] = email
                flash("Password reset OTP sent to your email.")
                return redirect(url_for("reset_password"))
            else:
                flash("Unable to send OTP email. Please check your mail settings.")
                return redirect(url_for("forgot_password"))

        except Exception as e:
            print("FORGOT PASSWORD ERROR:", str(e))
            flash("Something went wrong while processing forgot password.")
            return redirect(url_for("forgot_password"))

    return render_template("forgot_password.html")


@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    email = session.get("reset_email")

    if not email:
        flash("Password reset session expired. Please try again.")
        return redirect(url_for("forgot_password"))

    if request.method == "POST":
        try:
            otp = request.form.get("otp", "").strip()
            new_password = request.form.get("new_password", "").strip()

            if not otp or not new_password:
                flash("Please enter both OTP and new password.")
                return redirect(url_for("reset_password"))

            if len(new_password) < 6:
                flash("Password must be at least 6 characters long.")
                return redirect(url_for("reset_password"))

            if verify_otp(email, otp, "reset"):
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute("""
                    UPDATE users
                    SET password = %s
                    WHERE email = %s
                """, (generate_password_hash(new_password), email))
                conn.commit()
                cur.close()
                conn.close()

                session.pop("reset_email", None)
                flash("Password reset successful. Please login.")
                return redirect(url_for("login"))
            else:
                flash("Invalid or expired OTP.")
                return redirect(url_for("reset_password"))

        except Exception as e:
            print("RESET PASSWORD ERROR:", str(e))
            flash("Something went wrong while resetting password.")
            return redirect(url_for("reset_password"))

    return render_template("reset_password.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out successfully.")
    return redirect(url_for("home"))


@app.route("/profile", methods=["GET", "POST"])
def profile():
    if not require_login():
        return redirect(url_for("login"))

    user_id = session["user_id"]

    if request.method == "POST":
        age = request.form.get("age") or None
        phone = request.form.get("phone")
        city = request.form.get("city")
        occupation = request.form.get("occupation")
        height_cm = request.form.get("height_cm") or None
        weight_kg = request.form.get("weight_kg") or None
        menstrual_cycle_length = request.form.get("menstrual_cycle_length") or None
        period_duration = request.form.get("period_duration") or None
        last_period_date = request.form.get("last_period_date") or None
        cycle_regular = int(request.form.get("cycle_regular", 1))
        notes = request.form.get("notes")

        existing = get_profile(user_id)

        conn = get_db_connection()
        cur = conn.cursor()

        if existing:
            cur.execute("""
                UPDATE user_profiles
                SET age=%s, phone=%s, city=%s, occupation=%s, height_cm=%s, weight_kg=%s,
                    menstrual_cycle_length=%s, period_duration=%s, last_period_date=%s,
                    cycle_regular=%s, notes=%s, updated_at=CURRENT_TIMESTAMP
                WHERE user_id=%s
            """, (
                age, phone, city, occupation, height_cm, weight_kg,
                menstrual_cycle_length, period_duration, last_period_date,
                cycle_regular, notes, user_id
            ))
        else:
            cur.execute("""
                INSERT INTO user_profiles (
                    user_id, age, phone, city, occupation, height_cm, weight_kg,
                    menstrual_cycle_length, period_duration, last_period_date,
                    cycle_regular, notes
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                user_id, age, phone, city, occupation, height_cm, weight_kg,
                menstrual_cycle_length, period_duration, last_period_date,
                cycle_regular, notes
            ))

        conn.commit()
        cur.close()
        conn.close()

        flash("Profile saved successfully.")
        return redirect(url_for("profile"))

    profile_data = get_profile(user_id)
    notifications = get_notifications(user_id)
    unread_count = get_unread_notification_count(user_id)

    return render_template(
        "profile.html",
        profile=profile_data,
        notifications=notifications,
        unread_count=unread_count
    )


@app.route("/bmi", methods=["GET", "POST"])
def bmi():
    if not require_login():
        return redirect(url_for("login"))

    if not require_stress_before_bmi():
        flash("Please complete the stress quiz first.")
        return redirect(url_for("stress_quiz"))

    bmi_result = None

    if request.method == "POST":
        height_cm = float(request.form["height_cm"])
        weight_kg = float(request.form["weight_kg"])
        bmi_value, bmi_category = calculate_bmi(height_cm, weight_kg)

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO bmi_records (user_id, height_cm, weight_kg, bmi_value, bmi_category)
            VALUES (%s, %s, %s, %s, %s)
        """, (session["user_id"], height_cm, weight_kg, bmi_value, bmi_category))
        conn.commit()
        cur.close()
        conn.close()

        bmi_result = (height_cm, weight_kg, bmi_value, bmi_category)

    latest_bmi = get_latest_bmi_record(session["user_id"])
    return render_template("bmi.html", bmi_result=bmi_result, latest_bmi=latest_bmi)


@app.route("/pcod_test")
def pcod_test():
    if not require_login():
        return redirect(url_for("login"))

    if not require_stress_before_bmi():
        flash("Please complete the stress quiz first.")
        return redirect(url_for("stress_quiz"))

    if not require_bmi_before_pcod():
        flash("Please complete the BMI calculator first.")
        return redirect(url_for("bmi"))

    profile_data = get_profile(session["user_id"])
    latest_stress = get_latest_stress_result_row(session["user_id"])
    latest_bmi = get_latest_bmi_record(session["user_id"])

    return render_template(
        "pcod_test.html",
        profile=profile_data,
        latest_stress=latest_stress,
        latest_bmi=latest_bmi
    )


@app.route("/predict_pcod", methods=["POST"])
def predict_pcod():
    if not require_login():
        return redirect(url_for("login"))

    try:
        age = float(request.form["age"])
        bmi = float(request.form["bmi"])
        cycle_regular = int(request.form["cycle_regular"])
        cycle_length_days = float(request.form["cycle_length_days"])
        weight_gain = int(request.form["weight_gain"])
        hair_growth = int(request.form["hair_growth"])
        skin_darkening = int(request.form["skin_darkening"])
        hair_loss = int(request.form["hair_loss"])
        acne = int(request.form["acne"])
        fast_food = int(request.form["fast_food"])
        exercise = int(request.form["exercise"])

        latest_stress = get_latest_stress_result_row(session["user_id"])
        stress_level = latest_stress[2] if latest_stress else request.form.get("stress_level", "Low")
        stress_score = stress_level_to_score(stress_level)

        form_data = {
            "age": age,
            "bmi": bmi,
            "cycle_regular": cycle_regular,
            "cycle_length_days": cycle_length_days,
            "weight_gain": weight_gain,
            "hair_growth": hair_growth,
            "skin_darkening": skin_darkening,
            "hair_loss": hair_loss,
            "acne": acne,
            "fast_food": fast_food,
            "exercise": exercise,
            "stress_score": stress_score
        }

        input_data = pd.DataFrame([{feature: form_data.get(feature, 0) for feature in model_features}])

        prediction = int(pcod_model.predict(input_data)[0])

        if hasattr(pcod_model, "predict_proba"):
            base_probability = float(pcod_model.predict_proba(input_data)[0][1]) * 100
        else:
            base_probability = 50.0 if prediction == 1 else 20.0

        if "stress_score" in model_features:
            final_probability = round(base_probability, 2)
            stress_note = "Stress is included directly as a model feature in this prediction."
            stored_stress_adjustment = 0.0
        else:
            final_probability = adjust_probability_with_stress(base_probability, stress_level)
            stress_note = "Stress is used here as a supportive adjustment factor, not as a clinically validated standalone accuracy improvement."
            stored_stress_adjustment = stress_adjustment_value(stress_level)

        result = risk_from_probability(final_probability)

        if result == "High Risk of PCOD":
            suggestions = [
                "Maintain a healthy weight through a balanced diet.",
                "Exercise regularly for at least 30 minutes a day.",
                "Reduce junk food and high-sugar intake.",
                "Track your menstrual cycle regularly.",
                "Consult a gynecologist for proper medical guidance."
            ]
        elif result == "Moderate Risk of PCOD":
            suggestions = [
                "Improve food quality and regular meal timing.",
                "Exercise consistently 4 to 5 days per week.",
                "Track menstrual changes and symptoms carefully.",
                "Reduce fast food and sugary foods.",
                "Consult a doctor if symptoms persist."
            ]
        else:
            suggestions = [
                "Continue following a healthy lifestyle.",
                "Eat balanced meals and stay hydrated.",
                "Exercise regularly to maintain hormonal balance.",
                "Monitor your menstrual cycle and symptoms.",
                "Visit a doctor if symptoms increase in the future."
            ]

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO pcod_tests (
                user_id, age, bmi, cycle_regular, cycle_length_days,
                weight_gain, hair_growth, skin_darkening, hair_loss,
                acne, fast_food, exercise, stress_level, stress_adjustment,
                predicted_risk, probability
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            session["user_id"], age, bmi, cycle_regular, cycle_length_days,
            weight_gain, hair_growth, skin_darkening, hair_loss,
            acne, fast_food, exercise, stress_level, stored_stress_adjustment,
            result, round(final_probability, 2)
        ))
        pcod_test_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        session["latest_pcod_test_id"] = pcod_test_id
        session["latest_pcod_risk"] = result
        session["latest_pcod_probability"] = round(final_probability, 2)

        create_notification(
            session["user_id"],
            "PCOD Test Completed",
            f"Your latest PCOD assessment result is {result} with {round(final_probability, 2)}% probability.",
            "success"
        )

        return render_template(
            "Result.html",
            result=result,
            probability=round(final_probability, 2),
            suggestions=suggestions,
            stress_level=stress_level,
            stress_accuracy_note=stress_note
        )

    except Exception as e:
        flash(f"Prediction error: {str(e)}")
        return redirect(url_for("pcod_test"))


@app.route("/latest_pcod_result")
def latest_pcod_result():
    if not require_login():
        return redirect(url_for("login"))

    latest = get_latest_pcod_test(session["user_id"])
    if not latest:
        flash("No PCOD result found. Please complete PCOD test first.")
        return redirect(url_for("pcod_test"))

    result = latest[1]
    probability = float(latest[2])

    if result == "High Risk of PCOD":
        suggestions = [
            "Maintain a healthy weight through a balanced diet.",
            "Exercise regularly for at least 30 minutes a day.",
            "Reduce junk food and high-sugar intake.",
            "Track your menstrual cycle regularly.",
            "Consult a gynecologist for proper medical guidance."
        ]
    elif result == "Moderate Risk of PCOD":
        suggestions = [
            "Improve food quality and regular meal timing.",
            "Exercise consistently 4 to 5 days per week.",
            "Track menstrual changes and symptoms carefully.",
            "Reduce fast food and sugary foods.",
            "Consult a doctor if symptoms persist."
        ]
    else:
        suggestions = [
            "Continue following a healthy lifestyle.",
            "Eat balanced meals and stay hydrated.",
            "Exercise regularly to maintain hormonal balance.",
            "Monitor your menstrual cycle and symptoms.",
            "Visit a doctor if symptoms increase in the future."
        ]

    if "stress_score" in model_features:
        stress_note = "Stress is included directly as a model feature in this prediction."
    else:
        stress_note = "Stress is used here as a supportive adjustment factor, not as a clinically validated standalone accuracy improvement."

    return render_template(
        "Result.html",
        result=result,
        probability=round(probability, 2),
        suggestions=suggestions,
        stress_level=latest[4],
        stress_accuracy_note=stress_note
    )


@app.route("/stress_quiz", methods=["GET", "POST"])
def stress_quiz():
    if not require_login():
        return redirect(url_for("login"))

    questions = get_stress_questions()

    if request.method == "POST":
        answers = []

        for i in range(len(questions)):
            value = int(request.form.get(f"q{i}", 0))
            answers.append(value)

        total_score = calculate_pss_score(answers)
        stress_level = calculate_stress_level(total_score)

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO stress_quiz_results (user_id, stress_score, stress_level, answers_json)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (session["user_id"], total_score, stress_level, json.dumps(answers)))

        stress_result_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        session["latest_stress_result_id"] = stress_result_id
        session["latest_stress_score"] = total_score
        session["latest_stress_level"] = stress_level

        create_notification(
            session["user_id"],
            "Stress Quiz Completed",
            f"Your stress result is {stress_level}.",
            "success"
        )

        return redirect(url_for("stress_result"))

    return render_template(
        "stress_quiz.html",
        questions=questions,
        weekly_due=weekly_stress_due(session["user_id"])
    )


@app.route("/stress_result")
def stress_result():
    if not require_login():
        return redirect(url_for("login"))

    stress_score = session.get("latest_stress_score")
    stress_level = session.get("latest_stress_level")

    if stress_score is None or stress_level is None:
        latest = get_latest_stress_result_row(session["user_id"])
        if not latest:
            flash("Please complete the stress quiz first.")
            return redirect(url_for("stress_quiz"))
        stress_score = latest[1]
        stress_level = latest[2]

    return render_template(
        "stress_result.html",
        stress_score=stress_score,
        stress_level=stress_level
    )


@app.route("/latest_stress_result")
def latest_stress_result():
    if not require_login():
        return redirect(url_for("login"))

    latest = get_latest_stress_result_row(session["user_id"])
    if not latest:
        flash("No stress result found. Please complete stress quiz first.")
        return redirect(url_for("stress_quiz"))

    return render_template(
        "stress_result.html",
        stress_score=latest[1],
        stress_level=latest[2]
    )


@app.route("/diet")
def diet():
    if not require_login():
        return redirect(url_for("login"))

    latest_pcod = get_latest_pcod_test(session["user_id"])
    latest_stress = get_latest_stress_result_row(session["user_id"])

    pcod_result = latest_pcod[1] if latest_pcod else None
    stress_level = latest_stress[2] if latest_stress else None

    diet_plan = generate_diet_plan(pcod_result, stress_level)

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO personalized_plans (user_id, pcod_test_id, stress_result_id, diet_plan, exercise_plan)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        session["user_id"],
        latest_pcod[0] if latest_pcod else None,
        latest_stress[0] if latest_stress else None,
        "\n".join(diet_plan),
        ""
    ))
    conn.commit()
    cur.close()
    conn.close()

    return render_template("Diet.html", diet_plan=diet_plan, risk=pcod_result, stress_level=stress_level)


@app.route("/exercise")
def exercise():
    if not require_login():
        return redirect(url_for("login"))

    latest_pcod = get_latest_pcod_test(session["user_id"])
    latest_stress = get_latest_stress_result_row(session["user_id"])

    pcod_result = latest_pcod[1] if latest_pcod else None
    stress_level = latest_stress[2] if latest_stress else None

    exercise_plan = generate_exercise_plan(pcod_result, stress_level)

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO personalized_plans (user_id, pcod_test_id, stress_result_id, diet_plan, exercise_plan)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        session["user_id"],
        latest_pcod[0] if latest_pcod else None,
        latest_stress[0] if latest_stress else None,
        "",
        "\n".join(exercise_plan)
    ))
    conn.commit()
    cur.close()
    conn.close()

    return render_template("exercise.html", exercise_plan=exercise_plan, risk=pcod_result, stress_level=stress_level)


@app.route("/dashboard")
def dashboard():
    if not require_login():
        return redirect(url_for("login"))

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT TO_CHAR(created_at, 'YYYY-MM-DD'), stress_score
        FROM stress_quiz_results
        WHERE user_id = %s
        ORDER BY created_at ASC
    """, (session["user_id"],))
    stress_rows = cur.fetchall()

    cur.execute("""
        SELECT TO_CHAR(created_at, 'YYYY-MM-DD'), bmi_value
        FROM bmi_records
        WHERE user_id = %s
        ORDER BY created_at ASC
    """, (session["user_id"],))
    bmi_rows = cur.fetchall()

    cur.execute("""
        SELECT TO_CHAR(created_at, 'YYYY-MM-DD'), probability
        FROM pcod_tests
        WHERE user_id = %s
        ORDER BY created_at ASC
    """, (session["user_id"],))
    pcod_rows = cur.fetchall()

    cur.close()
    conn.close()

    latest_pcod = get_latest_pcod_test(session["user_id"])
    latest_stress = get_latest_stress_result_row(session["user_id"])
    latest_bmi = get_latest_bmi_record(session["user_id"])

    return render_template(
        "Dashboard.html",
        name=session.get("user_name"),
        latest_pcod=latest_pcod,
        latest_stress=latest_stress,
        latest_bmi=latest_bmi,
        stress_labels=[r[0] for r in stress_rows],
        stress_values=[int(r[1]) for r in stress_rows],
        bmi_labels=[r[0] for r in bmi_rows],
        bmi_values=[float(r[1]) for r in bmi_rows],
        pcod_labels=[r[0] for r in pcod_rows],
        pcod_values=[float(r[1]) for r in pcod_rows]
    )


@app.route("/mark_notifications_read")
def mark_notifications_read_route():
    if not require_login():
        return redirect(url_for("login"))
    mark_all_notifications_read(session["user_id"])
    return redirect(url_for("home"))


@app.route("/about")
def about():
    return render_template("About.html")


@app.route("/faq")
def faq():
    return render_template("FAQ.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        subject_text = request.form.get("subject", "").strip()
        message_text = request.form.get("message", "").strip()

        if not name:
            name = session.get("user_name", "User")

        if not email:
            email = session.get("user_email", "").strip().lower()

        if not subject_text:
            subject_text = "General Query"

        if not email or not message_text:
            flash("Please fill in email and message.")
            return redirect(url_for("contact"))

        admin_sent = send_contact_email_to_admin(name, email, subject_text, message_text)

        if admin_sent:
            send_contact_ack_email(email, name, subject_text)
            flash("Your message has been sent successfully.")
        else:
            flash("Message sending failed. Try again later.")

        return redirect(url_for("contact"))

    return render_template("Contact.html")


@app.route("/chatbot")
def chatbot():
    if not require_login():
        return redirect(url_for("login"))
    return render_template("chatbot.html")


@app.route("/api/chatbot", methods=["POST"])
def chatbot_api():
    if not is_logged_in():
        return jsonify({"error": "Please login first."}), 401

    current_user = get_user_by_id(session["user_id"])
    if not current_user:
        session.clear()
        return jsonify({"error": "Session expired. Please login again."}), 401

    data = request.get_json(silent=True) or {}
    user_message = str(data.get("message", "")).strip()

    if not user_message:
        return jsonify({"error": "Message is required."}), 400

    try:
        chatbot_service = get_chatbot_service()
        user_context = get_user_health_context(session["user_id"])
        result = chatbot_service.get_response(user_message, user_context)
        result["user_context"] = user_context
        return jsonify(result)

    except FileNotFoundError as e:
        return jsonify({"error": f"Chatbot model not found: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Chatbot error: {str(e)}"}), 500


@app.route("/combined_health_data")
def combined_health_data():
    if "user_id" not in session:
        return jsonify({"labels": [], "pcod": [], "stress": []})

    user_id = session["user_id"]

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT DATE_TRUNC('month', created_at) as dt,
               ROUND(AVG(probability), 2)
        FROM pcod_tests
        WHERE user_id = %s
        GROUP BY dt
        ORDER BY dt
    """, (user_id,))
    pcod_rows = cur.fetchall()

    cur.execute("""
        SELECT DATE_TRUNC('month', created_at) as dt,
               ROUND(AVG(stress_score), 2)
        FROM stress_quiz_results
        WHERE user_id = %s
        GROUP BY dt
        ORDER BY dt
    """, (user_id,))
    stress_rows = cur.fetchall()

    cur.execute("""
        SELECT probability FROM pcod_tests
        WHERE user_id = %s
        ORDER BY created_at DESC LIMIT 1
    """, (user_id,))
    latest_pcod = cur.fetchone()

    cur.execute("""
        SELECT stress_score FROM stress_quiz_results
        WHERE user_id = %s
        ORDER BY created_at DESC LIMIT 1
    """, (user_id,))
    latest_stress = cur.fetchone()

    cur.close()
    conn.close()

    pcod_dict = {row[0].date(): float(row[1]) for row in pcod_rows}
    stress_dict = {row[0].date(): float(row[1]) for row in stress_rows}

    all_dates = sorted(set(pcod_dict.keys()) | set(stress_dict.keys()))

    labels = []
    pcod_values = []
    stress_values = []

    for dt in all_dates:
        labels.append(dt.strftime("%b %Y"))
        pcod_values.append(pcod_dict.get(dt, None))
        stress_values.append(stress_dict.get(dt, None))

    return jsonify({
        "labels": labels,
        "pcod": pcod_values,
        "stress": stress_values,
        "latest_pcod": latest_pcod[0] if latest_pcod else None,
        "latest_stress": latest_stress[0] if latest_stress else None
    })


@app.context_processor
def inject_notifications():
    if "user_id" in session:
        return {
            "notifications": get_notifications(session["user_id"]),
            "unread_count": get_unread_notification_count(session["user_id"])
        }
    return {}


@app.route("/download_report")
def download_report():
    if not require_login():
        return redirect(url_for("login"))

    user_id = session["user_id"]

    latest_pcod = get_latest_pcod_test(user_id)
    latest_stress = get_latest_stress_result_row(user_id)
    profile = get_profile(user_id)

    diet_plan = generate_diet_plan(
        latest_pcod[1] if latest_pcod else None,
        latest_stress[2] if latest_stress else None
    )

    exercise_plan = generate_exercise_plan(
        latest_pcod[1] if latest_pcod else None,
        latest_stress[2] if latest_stress else None
    )

    os.makedirs(app.static_folder, exist_ok=True)
    graph_path = os.path.join(app.static_folder, "report_graph.png")

    latest_pcod_value = float(latest_pcod[2]) if latest_pcod else 0
    latest_stress_value = float(latest_stress[1]) if latest_stress else 0

    x = [0, 1]
    pcod_values = [0, latest_pcod_value]
    stress_values = [0, latest_stress_value]

    plt.figure(figsize=(6, 4))
    plt.plot(x, pcod_values, marker='o')
    plt.plot(x, stress_values, marker='o')
    plt.xticks([0, 1], ["Start", "Current"])
    plt.title("Health Status")
    plt.ylabel("Score (%)")
    plt.legend(["PCOD", "Stress"])
    plt.grid(True)
    plt.savefig(graph_path)
    plt.close()

    graph_url = graph_path

    rendered = render_template(
        "report_template.html",
        name=session.get("user_name"),
        age=profile[2] if profile else "N/A",
        phone=profile[3] if profile else "N/A",
        date=datetime.now().strftime("%d %B %Y"),
        pcod=latest_pcod[1] if latest_pcod else "N/A",
        pcod_prob=latest_pcod[2] if latest_pcod else "N/A",
        stress=latest_stress[2] if latest_stress else "N/A",
        stress_score=latest_stress[1] if latest_stress else "N/A",
        diet=diet_plan,
        exercise=exercise_plan,
        graph_url=graph_url
    )

    options = {
        "enable-local-file-access": None
    }

    pdf = pdfkit.from_string(
        rendered,
        False,
        configuration=pdfkit_config,
        options=options
    )

    return Response(
        pdf,
        mimetype="application/pdf",
        headers={"Content-Disposition": "attachment;filename=report.pdf"}
    )


if __name__ == "__main__":
    app.run(debug=True)