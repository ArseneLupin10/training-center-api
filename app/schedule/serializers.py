"""
Serializers for the schedule API
"""

from rest_framework import serializers
from schedule.models import(
    ClassRoom,
    CourseTime,
    Schedule,
    Day,
)
from course.models import Course
import sys
from django.db.models import Q



class ClassRoomSerializer(serializers.ModelSerializer):
    """serializer for the ClassRoim model"""

    class Meta:
        model = ClassRoom
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    """Serializer for the course field"""
    class Meta:
        model = Course
        fields = ['id', 'name', 'instructor']


class CourseTimeSerializer(serializers.ModelSerializer):
    """Serializer for the coursetime model"""
    course = CourseSerializer(read_only=True)
    classroom = ClassRoomSerializer(read_only=True)
    class Meta:
        model = CourseTime
        fields = '__all__'



class CourseTimeSerializerV2(serializers.ModelSerializer):
    """another version of the coursetime
    serializer without nested serializers"""
    class Meta:
        model = CourseTime
        fields = '__all__'


class CourseTimeDaySerializer(serializers.Serializer):
    """link the day to the coursetime serializer"""
    day = serializers.CharField(max_length=255)
    course = serializers.IntegerField()
    classroom = serializers.IntegerField()
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()

    def create(self, validated_data):
        """create a coursetime inside the schedule"""
        day = validated_data.pop('day', None)
        course_id = validated_data.pop('course')
        classroom_id = validated_data.pop('classroom')

        try:
            course_instance = Course.objects.get(id=course_id)
            classroom_instance = ClassRoom.objects.get(id=classroom_id)
        except (Course.DoesNotExist, ClassRoom.DoesNotExist) as e:
            raise serializers.ValidationError(f"Invalid course or classroom ID: {e}")



        if day:
            schedule_instance = Schedule.objects.first()
            schedule_day = getattr(schedule_instance, f"{day.lower()}")
            course_times= schedule_day.filter(classroom=classroom_instance)
            start_time = validated_data['start_time']
            end_time = validated_data['end_time']
            overlapping_course_times = course_times.filter(
            Q(start_time__lte=start_time, end_time__gte=start_time) |  # Check if new start time falls within existing range
            Q(start_time__lte=end_time, end_time__gte=end_time) |      # Check if new end time falls within existing range
            Q(start_time__gte=start_time, end_time__lte=end_time)      # Check if new range fully encapsulates existing range
            )

            if overlapping_course_times:
                raise serializers.ValidationError("Time is taken ")

            coursetime_instance = CourseTime.objects.create(
            course=course_instance,
            classroom=classroom_instance,
            **validated_data
            )
            schedule_day.add(coursetime_instance)



        return coursetime_instance





class DaySerializer(serializers.ModelSerializer):
    """Serializer for the Day model"""
    class Meta:
        model = Day


class ScheduleSerializer(serializers.ModelSerializer):
    """Serializer for the schedule model"""
    saturday = CourseTimeSerializer(many=True, required=False)
    sunday = CourseTimeSerializer(many=True, required=False)
    monday = CourseTimeSerializer(many=True, required=False)
    tuesday = CourseTimeSerializer(many=True, required=False)
    wednesday = CourseTimeSerializer(many=True, required=False)
    thuresday = CourseTimeSerializer(many=True, required=False)
    friday = CourseTimeSerializer(many=True, required=False)
    class Meta:
        model = Schedule
        fields = '__all__'

    def to_representation(self, instance):
        """Order CourseTime instances before serializing"""
        representation = super().to_representation(instance)

        # Iterate over each day field and order CourseTime instances
        for day in ['saturday', 'sunday', 'monday', 'tuesday', 'wednesday', 'thuresday', 'friday']:
            representation[day] = self.order_course_times(representation[day])

        return representation

    def order_course_times(self, course_times):
        """Order CourseTime instances by start_time"""
        ordered_course_times = sorted(course_times, key=lambda x: x['start_time'])
        return ordered_course_times
