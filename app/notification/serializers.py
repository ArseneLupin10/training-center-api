"""
Serializers for the notification model
"""


from rest_framework import serializers
from notification.models import Notification
from course.models import Course


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer to display a notification"""
    class Meta:
        model = Notification
        fields = ['id', 'message']


class DescisionSerializer(serializers.Serializer):
    """Serializer for the notification
    response"""

    descision = serializers.BooleanField()
    notification_id = serializers.IntegerField()

    def create(self, validated_data):
        """close or keep courses registration
        open based on the descision"""

        notification = Notification.objects.get(id=validated_data['notification_id'])
        course_id = notification.course.id
        course = Course.objects.get(id=course_id)
        if validated_data['descision']:
            course.registration_open = False
            course.save()
            message = 'registration closed'
            return message

        message = 'registration still open'

        return message