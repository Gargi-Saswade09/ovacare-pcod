from datetime import datetime, timedelta
from urllib.parse import quote


def google_calendar_link(title, details, start_dt, end_dt):
    def fmt(dt):
        return dt.strftime("%Y%m%dT%H%M%S")

    base = "https://calendar.google.com/calendar/render?action=TEMPLATE"
    return (
        f"{base}"
        f"&text={quote(title)}"
        f"&details={quote(details)}"
        f"&dates={fmt(start_dt)}/{fmt(end_dt)}"
    )


def weekly_stress_quiz_calendar_link():
    start_dt = datetime.now() + timedelta(days=7)
    end_dt = start_dt + timedelta(minutes=20)
    return google_calendar_link(
        "Weekly Stress Quiz - OvaCare",
        "Complete your weekly stress quiz on OvaCare.",
        start_dt,
        end_dt
    )


def monthly_pcod_test_calendar_link():
    start_dt = datetime.now() + timedelta(days=30)
    end_dt = start_dt + timedelta(minutes=25)
    return google_calendar_link(
        "Monthly PCOD Test - OvaCare",
        "Complete your monthly PCOD tracking form on OvaCare.",
        start_dt,
        end_dt
    )