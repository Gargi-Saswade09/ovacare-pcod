from datetime import datetime, timedelta
from database.db import get_db_connection


def create_notification(user_id, title, message, ntype="info"):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO notifications (user_id, title, message, type)
        VALUES (%s, %s, %s, %s)
    """, (user_id, title, message, ntype))
    conn.commit()
    cur.close()
    conn.close()


def get_notifications(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM notifications
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT 20
    """, (user_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def mark_notification_read(notification_id, user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE notifications
        SET is_read = TRUE
        WHERE id = %s AND user_id = %s
    """, (notification_id, user_id))
    conn.commit()
    cur.close()
    conn.close()


def get_last_stress_quiz_date(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT created_at
        FROM stress_quiz_results
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT 1
    """, (user_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row["created_at"] if row else None


def get_last_pcod_test_date(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT created_at
        FROM pcod_tests
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT 1
    """, (user_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row["created_at"] if row else None


def ensure_due_notifications(user_id):
    now = datetime.now()

    last_stress = get_last_stress_quiz_date(user_id)
    if not last_stress or now - last_stress >= timedelta(days=7):
        create_notification(
            user_id,
            "Weekly Stress Quiz Due",
            "Your weekly stress quiz is due. Please complete it for updated recommendations.",
            "warning"
        )

    last_pcod = get_last_pcod_test_date(user_id)
    if not last_pcod or now - last_pcod >= timedelta(days=30):
        create_notification(
            user_id,
            "Monthly PCOD Test Due",
            "Your monthly PCOD self-assessment is due. Please complete it for updated tracking.",
            "warning"
        )