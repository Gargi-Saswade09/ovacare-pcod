import os

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", "pcod_system"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
    "port": os.getenv("DB_PORT", "5432")
}

SECRET_KEY = os.getenv("SECRET_KEY", "ovacare_secret_key_123")

MAIL_CONFIG = {
    "sender_email": os.getenv("OVACARE_SENDER_EMAIL", ""),
    "sender_password": os.getenv("OVACARE_SENDER_PASSWORD", ""),
    "smtp_server": os.getenv("OVACARE_SMTP_SERVER", "smtp.gmail.com"),
    "smtp_port": int(os.getenv("OVACARE_SMTP_PORT", "587")),
    "admin_email": os.getenv("OVACARE_ADMIN_EMAIL", os.getenv("OVACARE_SENDER_EMAIL", "")),
    "site_name": os.getenv("OVACARE_SITE_NAME", "OvaCare")
}