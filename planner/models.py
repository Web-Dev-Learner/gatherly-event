from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime


class Event(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=300)
    guest_emails = models.TextField(help_text="Comma-separated emails")
    video_link = models.URLField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  
    reminder_sent = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    def start_datetime(self):
        return timezone.make_aware(datetime.combine(self.date, self.time))

    def __str__(self):
        return f"{self.title} on {self.date}"


class RSVP(models.Model):
    RESPONSE_CHOICES = [
        ('yes', 'Going'),
        ('no', 'No'),
        ('maybe', 'Maybe'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='rsvps')
    response = models.CharField(max_length=10, choices=RESPONSE_CHOICES)
    note = models.TextField(blank=True)
    responded_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'event')
