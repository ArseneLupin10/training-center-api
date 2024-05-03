"""
Serializers for the teacher view
"""

from rest_framework import serializers
from teacher.models import Teacher
from course.serializers import CourseSerializer



class TeacherSerializer(serializers.ModelSerializer):
    """serializer for the teacher"""
    class Meta:
        model = Teacher
        fields = ['id', 'email', 'first_name', 'last_name','image']
        read_only_fields = ['id']


class AppTeacher(TeacherSerializer):
    """teacher in the app"""
    class Meta(TeacherSerializer.Meta):
        fields = TeacherSerializer.Meta.fields + ['bio', 'about']


class DetailAppTeacher(AppTeacher):
    """Detailed teacher in the app"""
    courses = CourseSerializer(many=True)
    class Meta(AppTeacher.Meta):
        fields = AppTeacher.Meta.fields + ['twitter', 'facebook', 'linked_in', 'youtube', 'courses']


class DetailDashboardTeacher(serializers.ModelSerializer):
    """Detail eacher in the dashboard"""
    courses = CourseSerializer(many=True, read_only=True)
    class Meta:
        model = Teacher
        fields = '__all__'
        read_only_fields = ['id', 'courses']