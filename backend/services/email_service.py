import smtplib
from email.message import EmailMessage
from config import MAIL_CONFIG


def send_email(to_email, subject, body, reply_to=None):
    sender_email = MAIL_CONFIG.get("sender_email")
    sender_password = MAIL_CONFIG.get("sender_password")
    smtp_server = MAIL_CONFIG.get("smtp_server", "smtp.gmail.com")
    smtp_port = MAIL_CONFIG.get("smtp_port", 587)

    if not sender_email or not sender_password:
        print("EMAIL ERROR: sender email or app password missing.")
        return False

    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = to_email

        if reply_to:
            msg["Reply-To"] = reply_to

        msg.set_content(body)

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(sender_email, sender_password)
            server.send_message(msg)

        return True

    except Exception as e:
        print("EMAIL SEND ERROR:", str(e))
        return False


def send_otp_email(receiver_email, otp_code, purpose="general"):
    site_name = MAIL_CONFIG.get("site_name", "OvaCare")
    subject = f"{site_name} OTP Verification"

    if purpose == "register":
        body = (
            f"Hello,\n\n"
            f"Your {site_name} registration OTP is: {otp_code}\n\n"
            f"This OTP will expire in 10 minutes.\n\n"
            f"If you did not request this, please ignore this email."
        )
    elif purpose == "reset":
        body = (
            f"Hello,\n\n"
            f"Your {site_name} password reset OTP is: {otp_code}\n\n"
            f"This OTP will expire in 10 minutes.\n\n"
            f"If you did not request this, please ignore this email."
        )
    else:
        body = (
            f"Hello,\n\n"
            f"Your {site_name} OTP is: {otp_code}\n\n"
            f"This OTP will expire in 10 minutes."
        )

    return send_email(receiver_email, subject, body)


def send_reminder_email(receiver_email, user_name, reminder_title, reminder_message):
    site_name = MAIL_CONFIG.get("site_name", "OvaCare")
    subject = f"{site_name} Reminder: {reminder_title}"

    body = (
        f"Hello {user_name},\n\n"
        f"This is a reminder from {site_name}.\n\n"
        f"{reminder_message}\n\n"
        f"Please log in to your account and complete it when possible.\n\n"
        f"Regards,\n"
        f"{site_name} Team"
    )

    return send_email(receiver_email, subject, body)


def send_contact_email_to_admin(name, user_email, subject_text, message_text):
    site_name = MAIL_CONFIG.get("site_name", "OvaCare")
    admin_email = MAIL_CONFIG.get("admin_email")

    if not admin_email:
        print("EMAIL ERROR: admin_email is not configured.")
        return False

    subject = f"{site_name} Contact Form: {subject_text}"

    body = (
        f"New contact form submission received.\n\n"
        f"Name: {name}\n"
        f"User Email: {user_email}\n"
        f"Subject: {subject_text}\n\n"
        f"Message:\n"
        f"{message_text}\n"
    )

    return send_email(
        to_email=admin_email,
        subject=subject,
        body=body,
        reply_to=user_email,
    )


def send_contact_ack_email(user_email, user_name, subject_text):
    site_name = MAIL_CONFIG.get("site_name", "OvaCare")
    subject = f"{site_name}: We received your message"

    body = (
        f"Hello {user_name},\n\n"
        f"We received your message regarding: {subject_text}\n\n"
        f"Our team will review it and get back to you if needed.\n\n"
        f"Thank you,\n"
        f"{site_name} Team"
    )

    return send_email(user_email, subject, body)