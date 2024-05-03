"""
Models for the notification API
"""

from django.db import models
from course.models import Course


class Notification(models.Model):
    """A notificaion in the system"""

    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
