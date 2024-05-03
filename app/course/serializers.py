"""
Serializers for the course API
"""

from rest_framework import serializers
from course.models import (
    Course,
    Tag,
    CourseStudent,
    Comment,
    Archive,
)
from schedule.models import CourseTime
from teacher.models import Teacher
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from notification.models import Notification
from schedule.models import ClassRoom
from django.db.models import Max


class CourseSerializer(serializers.ModelSerializer):
    """serializer for the course model"""
    class Meta:
        model = Course
        fields = ['id', 'name', 'price', 'image']


class TagSerializer(serializers.ModelSerializer):
    """serializer for the tag model"""
    class Meta:
        model = Tag
        fields = '__all__'


class StudentSerializer(serializers.ModelSerializer):
    """Serializer for the student"""
    class Meta:
        model = get_user_model()
        fields = ['id', 'email', 'first_name', 'last_name', 'image']


class CourseStudentListSerializer(serializers.ListSerializer):
    """list serializer used for updating multiple
    instances at the same time"""
    def update(self, instance, validated_data):
        """update  the instances all at once """
        course_students = instance.students.all()
        new_course_students = validated_data
        # Extract IDs of existing course students
        existing_ids = [course_student.id for course_student in course_students]
        for new_course_student in new_course_students:
            if new_course_student['id'] in existing_ids:
                course_student_instance = CourseStudent.objects.get(id=
                                                                    new_course_student['id'])
                course_student_instance.paid = new_course_student['paid']
                course_student_instance.save()
            else:
                 raise Exception("unvalid course_student id ")
        return instance.students.all()


class CourseStudentSerializer(serializers.ModelSerializer):
    """serializer to represent student in the course"""
    student = StudentSerializer(read_only=True)
    id = serializers.IntegerField()
    class Meta:
        model=CourseStudent
        fields = '__all__'
        read_only_fields = ['students']
        list_serializer_class = CourseStudentListSerializer




class TeacherSerializer(serializers.ModelSerializer):
    """serializer for the teacher"""
    id = serializers.IntegerField(read_only=False)
    class Meta:
        model = Teacher
        fields = ['id', 'email', 'first_name', 'last_name','image']
        read_only_fields = ['email', 'first_name', 'last_name','image']



class DetailCourseSerializer(serializers.ModelSerializer):
    """Detailed Course serializer used for creation"""
    tags = serializers.ListField(child=serializers.CharField(max_length=100))
    class Meta:
        model = Course
        fields = ['id', 'image', 'name',  'bio', 'description', 'instructor', 'tags',
                  'price', 'registration_open', 'in_progress']


    def _get_or_create_tags(self, tags, course):
        """handle getting or creating tags as needed"""
        for tag in tags :
            tag_obj, _ = Tag.objects.get_or_create(name=tag)
            course.tags.add(tag_obj)


    def create(self, validated_data):
        """create a course"""
        tags = validated_data.pop('tags', [])
        course = Course.objects.create(**validated_data)
        self._get_or_create_tags(tags, course)

        return course

    def update(self, instance, validated_data):
        """update a course"""
        tags = validated_data.pop('tags', None)

        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance



class DetailCourseSerializerv2(serializers.ModelSerializer):
    """special detailed serializer for the response"""
    tags = TagSerializer(many=True, required=False)
    instructor = TeacherSerializer()
    students = CourseStudentSerializer(many=True)
    class Meta:
        model = Course
        fields = '__all__'

    def _get_or_create_tags(self, tags, course):
        """handle getting or creating tags as needed"""
        for tag in tags :
            tag_obj, _ = Tag.objects.get_or_create(**tag)
            course.tags.add(tag_obj)

    def create(self, validated_data):
        """create a course"""
        tags = validated_data.pop('tags', [])
        course = Course.objects.create(**validated_data)
        self._get_or_create_tags(tags, course)

        return course

    def update(self, instance, validated_data):
        """update a course"""
        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class AddStudentToCourseSerializer(serializers.Serializer):
    """serializer to use in the dashboard for
    adding a student to a course"""

    student_id = serializers.IntegerField()
    course_id = serializers.IntegerField()

    def create(self, validated_data):
        """Add student to course"""
        student = get_user_model().objects.get(id=validated_data['student_id'])
        course = Course.objects.get(id=validated_data['course_id'])

        if course.students.filter(student=student).exists():
            raise serializers.ValidationError("Student is already enrolled in the course")
        course_student = CourseStudent.objects.create(student=student)
        course.students.add(course_student)
        max_capacity = ClassRoom.objects.aggregate(max_capacity=Max('capacity'))
        max_capacity = max_capacity['max_capacity']
        print(f"Number of students: {course.students.count()}, Max capacity: {max_capacity}")


        if course.students.count() == max_capacity:
            message = f"""{course.students.count()} students registered to {course.name}/{course.instructor.first_name} {course.instructor.last_name} close registration ?"""
            Notification.objects.create(course=course, message=message)

        return course


class RemoveStudentFromCourseSerializer(serializers.Serializer):
    """serializer to use in the dashboard to remove
       a student from a course"""

    student_id = serializers.IntegerField()
    course_id = serializers.IntegerField()

    def create(self, validated_data):
        """remove student from course"""
        student = get_user_model().objects.get(id=validated_data['student_id'])
        course = Course.objects.get(id=validated_data['course_id'])

        if course.students.filter(student=student).exists():
            course.students.filter(student=student).first().delete()
        return course


class MobileAppTeacherSerializer(serializers.ModelSerializer):
    """Serializer for the teacher in the mobile app"""
    class Meta:
        model = Teacher
        fields = ['id', 'first_name', 'last_name', 'bio', 'image', 'about']


class TempTeacherSerializer(serializers.ModelSerializer):
    """Temp serializer for the teacher """
    class Meta:
        model = Teacher
        fields = ['first_name', 'last_name']


class MobileAppCourseSerializer(serializers.ModelSerializer):
    """Serializer for the course in the mobile app"""
    instructor = TempTeacherSerializer()
    class Meta:
        model = Course
        fields = ['id', 'image', 'name','price', 'instructor', 'rating']


class PostCommentSerializer(serializers.ModelSerializer):
    """Serializer for comment posting"""
    class Meta:
        model = Comment
        fields = ['comment', 'rating']

    def create(self, validated_data):
        """update the rating of the course"""
        instance = super().create(validated_data)
        request = self.context.get('request')
        course_id = request.parser_context['kwargs']['pk']
        course = Course.objects.get(id=course_id)
        course.rating = (validated_data['rating']+course.rating)/2
        course.save()

        return instance





class StudentCommentSerializer(serializers.ModelSerializer):
    """Serializer for the student of the comment"""
    class Meta:
        model = get_user_model()
        fields = ['id', 'image', 'first_name', 'last_name']


class GetCommentSerializer(serializers.Serializer):
    """Serializer for comment section"""
    student = StudentCommentSerializer(read_only=True)
    comment = serializers.CharField()
    rating = serializers.DecimalField(decimal_places = 1,
                                     max_digits =2,)
    read_only_fields = ['student', 'comment', 'rating']



class MobileAppDetailCourseSerializer(serializers.ModelSerializer):
    """serializer for the course in the mobile app"""
    tags = TagSerializer(many=True)
    comments = GetCommentSerializer(many=True)
    instructor = MobileAppTeacherSerializer()
    ratings = serializers.SerializerMethodField()

    def get_ratings(self, obj):
        """method to calculate and return ratings"""
        course_id = obj.id
        comments = Comment.objects.filter(course__id=course_id)
        total_comments = comments.count()
        if total_comments == 0:
            return {
                'one': 0,
                'two': 0,
                'three': 0,
                'four': 0,
                'five': 0,
                'total_rating': 0
            }

        ratings = [comment.rating for comment in comments]
        total_rating = sum(ratings)/total_comments
        course = Course.objects.get(id=course_id)
        course.rating = total_rating
        course.save()

        #Calculate percentage of every rating
        rating_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        int_ratings = [int(rating) for rating in ratings]
        for rating in int_ratings:
            rating_counts[rating]+=1
        percent_ratings = {str(rating): (count / total_comments) * 100 for rating, count in rating_counts.items()}

        return {
            'one': f"{percent_ratings.get('1', 0)}%",
            'two': f"{percent_ratings.get('2', 0)}%",
            'three': f"{percent_ratings.get('3', 0)}%",
            'four': f"{percent_ratings.get('4', 0)}%",
            'five': f"{percent_ratings.get('5', 0)}%",
            'total_rating': total_rating
        }
    class Meta:
        model = Course
        fields = ['id', 'image', 'name', 'bio', 'description', 'price', 'tags',
                   'instructor', 'comments', 'ratings']


class RegisterSerializer(serializers.Serializer):
    """serializer for course registration"""

    id = serializers.IntegerField()

    def create(self, validated_data):
        """Add student to the course
        and add course to the student"""

        student = self.context['request'].user
        course_student = CourseStudent.objects.create(student=student)
        course = Course.objects.get(id=validated_data['id'])
        if course.students.filter(student=student).exists():
            raise serializers.ValidationError("Student is already enrolled in the course")
        course.students.add(course_student)
        ax_capacity = ClassRoom.objects.aggregate(max_capacity=Max('capacity'))
        max_capacity = max_capacity['max_capacity']

        if course.students.count() >= max_capacity:
            message = f"""{course.students.count()} students registered to {course.name}/{course.instructor.first_name} {course.instructor.last_name} close registration ?"""
            Notification.objects.create(course=course, message=message)

        return student



class ArchiveSerializer(serializers.ModelSerializer):
    """Serializer for the archive of the course"""
    students = StudentCommentSerializer(many=True, read_only=True)
    class Meta:
        model = Archive
        fields = ['course_version', 'course_price', 'students', 'total_students', 'total_earnings']
        read_only_fields = ['course_version', 'course_price', 'students', 'total_students', 'total_earnings']

    def create(self, validated_data):
        """clear the course and save its data
        to an archeive instance"""

        request = self.context.get('request')
        course_id = request.parser_context['kwargs']['pk']
        course = Course.objects.get(id=course_id)
        if course.in_progress:
            students = course.students.filter(paid=True)
            course_price = course.price
            total_students = course.students.filter(paid=True).count()
            total_earnings = total_students*course_price
            course_version = Archive.objects.filter(course=course).count()+1
            archive = Archive.objects.create(course=course,
                                            course_price=course_price,
                                            total_students=total_students,
                                            total_earnings=total_earnings,
                                            course_version=course_version)
            for student in students:
                archive.students.add(student.student)

            course.students.all().delete()
            CourseTime.objects.filter(course=course).delete()
            course.in_progress = False
            course.save()

        else:
            raise Exception('course is not in progress')

        return archive
