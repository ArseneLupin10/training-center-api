"""
Models for the course
"""

from django.db import models
from teacher.models import Teacher
from user.models import User
import os
import uuid
from django.core.validators import MinValueValidator, MaxValueValidator


def image_file_path(instance, filename):
    """Generate filepath for new users"""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'
    return os.path.join('uploads', 'courses', filename)


class Course(models.Model):
    """a course in the system"""

    name = models.CharField(max_length=255)
    bio = models.CharField(max_length=255, blank=True, default = '')
    description = models.CharField(max_length=255, default = '', blank=True)
    price = models.DecimalField(decimal_places=5, max_digits=10)
    instructor = models.ForeignKey(
        Teacher,
        on_delete = models.CASCADE,
        related_name = 'courses',
        blank=True,
    )
    image = models.ImageField(default='', blank=True, upload_to=image_file_path)
    tags = models.ManyToManyField('Tag', blank=True, default='')
    registration_open = models.BooleanField(default=False)
    in_progress = models.BooleanField(default=False)

    status_choices = [
    ('all_levels', 'All_levels'),
    ('beginner', 'Beginner'),
    ('intermediate', 'Intermediate'),
    ('expert', 'Expert'),
    ]

    level = models.CharField(max_length=20, choices=status_choices, default='all_levels')
    rating = models.DecimalField(decimal_places =1, max_digits =2, default=3)
    students = models.ManyToManyField(
        'coursestudent',
        related_name='courses',
        blank=True,
        null=True,
    )
    def __str__(self):
        return f'{self.name}, {self.instructor}'


class CourseStudent(models.Model):
    """a student in the course"""
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='course_student',
        blank=True,
        null=True,
    )
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.student.first_name} {self.student.last_name}'


class Tag(models.Model):
    """Tags for filtering the courses"""
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Comment(models.Model):
    """comments for a course"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE,
                               related_name='comments')

    student = models.ForeignKey(User, on_delete=models.CASCADE,
                                related_name='comments')
    comment = models.CharField(max_length=255)
    rating = models.DecimalField(decimal_places = 1,
                                 max_digits =2,
                                 default = 3,
                                 validators=[
                                MinValueValidator(1),  # Minimum value
                                MaxValueValidator(5),  # Maximum value
                                ])


class Archive(models.Model):
    """Archive for a course"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE,
                               related_name='archive')
    course_version = models.IntegerField()
    students = models.ManyToManyField(User, related_name='history')
    course_price = models.DecimalField(decimal_places=5, max_digits=10)
    total_earnings = models.DecimalField(decimal_places=5, max_digits=10)
    total_students = models.IntegerField()