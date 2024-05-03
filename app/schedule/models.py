"""
Models for the schedule
"""

from django.db import models
from course.models import Course


class ClassRoom(models.Model):
    """a classroom in the center"""
    name = models.CharField(max_length = 255)
    capacity = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.name} , {self.capacity}'


class CourseTime(models.Model):
    """model to distribute courses to classrooms and times"""
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='course_times'
    )

    classroom = models.ForeignKey(
        ClassRoom,
        on_delete=models.CASCADE,
        related_name='classroom_times'
    )

    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f'{self.course}/{self.classroom}/{self.start_time} : {self.end_time}'


class Day(models.Model):
    name = models.CharField(max_length=10)
    def __str__(self):
        return self.name


class Schedule(models.Model):
    """schedule for classrooms and courses"""
    saturday = models.ManyToManyField('CourseTime', blank=True, related_name='saturday_courses')
    sunday = models.ManyToManyField('CourseTime', blank=True, related_name='sunday_courses')
    monday = models.ManyToManyField('CourseTime', blank=True, related_name='monday_courses')
    tuesday = models.ManyToManyField('CourseTime', blank=True, related_name='tuesday_courses')
    wednesday = models.ManyToManyField('CourseTime', blank=True, related_name='wednesday_courses')
    thuresday = models.ManyToManyField('CourseTime', blank=True, related_name='thuresday_courses')
    friday = models.ManyToManyField('CourseTime', blank=True, related_name='friday_courses')
