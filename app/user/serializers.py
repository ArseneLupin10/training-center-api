"""
Serializers for the user view
"""

from django.contrib.auth import(
    get_user_model,
    authenticate,
)
from rest_framework import serializers
from course.models import CourseStudent
from course.serializers import CourseSerializer


class AppUserSerializer(serializers.ModelSerializer):
    """Serializer for the app user"""

    class Meta:
        model = get_user_model()
        fields = ['id', 'email', 'first_name', 'last_name','password', 'image' , 'gender']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}
        read_only_fields = ['id']

    def create(self, validated_data):
        """create and return app-user with encrypted password"""
        user = get_user_model().objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        """update and return app-user"""
        password = validated_data.pop('password', None)
        image = validated_data.pop('image', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
        if image:
            user.image = image
        user.save()
        return user

class CourseStudentSerializer(serializers.ModelSerializer):
    """serializer that links studen to the courses"""
    courses = CourseSerializer(many=True, read_only=True)
    class Meta:
        model = CourseStudent
        fields = ['paid', 'courses']


class DetailAppUserSerializer(AppUserSerializer):
    """Detailed Serializer for the app user"""
    course_student = CourseStudentSerializer(many=True, read_only=True)
    class Meta(AppUserSerializer.Meta):
        fields = AppUserSerializer.Meta.fields+['address', 'phone_number', 'gender', 'birth_day', 'course_student']


class DashboardUserSerializer(serializers.ModelSerializer):
    """Serializer for the dashboard user"""

    class Meta:
        model = get_user_model()
        fields = ['id', 'email', 'first_name', 'last_name', 'image', 'is_superuser','is_staff', 'password']
        extra_kwargs = {'password' : {'write_only' : True, 'min_length': 5}}

    def create(self, validated_data):
        """create and return a staff or superuser"""
        is_superuser = validated_data.get('is_superuser')

        if is_superuser:
            return get_user_model().objects.create_superuser(**validated_data)
        else:
            return get_user_model().objects.create_staff(**validated_data)


class DetailDashboardUser(DashboardUserSerializer):
    """serilizer for the detailed dahsboard user"""
    class Meta(DashboardUserSerializer.Meta):
        fields = DashboardUserSerializer.Meta.fields+['address', 'phone_number', 'gender', 'birth_day']



class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the auth token in the app"""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type' : 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """Validate and authenticate the user"""
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )
        if not user :
            msg = 'Unable to authenticate with provided credentials'
            raise serializers.ValidationError(msg, code='authorization')

        if user.is_staff or user.is_superuser:
            msg = 'Unable to authenticate with provided credentials'
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs

class DashboardTokenSerializer(serializers.Serializer):
    """Serializer for the auth token in the dashboard"""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type' : 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """Validate and authenticate the user"""
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )
        if not user :
            msg = 'Unable to authenticate with provided credentials'
            raise serializers.ValidationError(msg, code='authorization')

        if user.is_staff==0 and user.is_superuser == 0:
            msg = 'Unable to authenticate with provided credentials'
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


