from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone

from .mailgun_email import send_mailgun_email
from datetime import datetime, timedelta
import pytz

# 🔒 Global variable to avoid duplicate scheduler
scheduler = None

def send_reminder_emails():
    from .models import Event
    print("⏰ Scheduler running: checking for events...")

    india_tz = pytz.timezone('Asia/Kolkata')
    now = timezone.now().astimezone(india_tz).replace(microsecond=0)
    one_hour_later = now + timedelta(hours=1)

    events = Event.objects.filter(
        reminder_sent=False,
        is_deleted=False,
        date__gte=now.date()
    )

    for event in events:
        event_datetime = datetime.combine(event.date, event.time)
        event_datetime = india_tz.localize(event_datetime).replace(microsecond=0)

        print(f"🎯 Now (IST): {now}, Event: {event_datetime}, 1hr Later: {one_hour_later}")

        margin = timedelta(minutes=1)
        if now - margin <= event_datetime <= one_hour_later + margin:
            subject = f"Reminder: Your event '{event.title}' starts in 1 hour"
            message = f"""Hi there,

This is a reminder that you're invited to the event:

Title: {event.title}
Time: {event.time}
Location: {event.location}

Join Video Call: {event.video_link}

- Gatherly Team
"""

            for email in event.guest_emails.split(","):
                email = email.strip()
                if email:
                    send_mailgun_email(email, subject, message)

            event.reminder_sent = True
            event.save()
            print(f"✅ Reminder sent for: {event.title}")

def start_scheduler():
    global scheduler
    if scheduler and scheduler.running:
        print("⚠️ Scheduler already running. Skipping duplicate.")
        return

    scheduler = BackgroundScheduler()
    scheduler.add_job(send_reminder_emails, 'interval', minutes=1)
    scheduler.start()
    print("✅ Scheduler started.")
