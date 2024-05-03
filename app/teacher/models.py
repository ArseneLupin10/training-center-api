"""
Teacher Model

"""


from django.db import models
from django.conf import settings
import os
import uuid


def image_file_path(instance, filename):
    """Generate filepath for new users"""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'
    return os.path.join('uploads', 'teachers', filename)



class Teacher(models.Model):
    """teacher in the system"""
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=11)
    address = models.CharField(max_length=255)
    birth_day = models.DateField(null=True)
    status_choices = [
    ('Male', 'Male'),
    ('Female', 'Female'),
    ]
    gender = models.CharField(max_length=7, choices=status_choices)
    bio = models.CharField(max_length=255, blank=True, null=True)
    about = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to=image_file_path, blank=True, null=True)
    linked_in = models.CharField(max_length=255, blank=True, null=True)
    facebook = models.CharField(max_length=255, blank=True, null=True)
    youtube = models.CharField(max_length=255, blank=True, null=True)
    twitter =  models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
