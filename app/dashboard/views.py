"""
Views for the dahboard

"""


from rest_framework.response import Response
from rest_framework import(
    viewsets,
    filters,
    generics,
    authentication,
    permissions,
    mixins
)
from user import serializers
from teacher import(
    models as teacher_models,
    serializers as teacher_serializers
)
from course import(
    models as course_models,
    serializers as course_serializers
)

from schedule import (
    serializers as schedule_serializers,
    models as schedule_models
)
from notification import (
    serializers as notification_serializers,
    models as notification_models
)
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from django.db.models import Q
from rest_framework.decorators import action
from rest_framework import status


@extend_schema_view(

    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'search',
                OpenApiTypes.STR,
                description='search'
            ),
        ]
    ),
)



class StudentViewSet(viewsets.ModelViewSet):
    """manage the student API"""
    serializer_class = serializers.DetailAppUserSerializer
    queryset = get_user_model().objects.filter(is_staff=False, is_superuser=False)
    filter_backends = (filters.SearchFilter,)
    search_fields=('email', 'first_name', 'last_name', 'phone_number', 'address')

    def get_serializer_class(self):
        """Return serializer class for the request"""
        if self.action == 'list':
            return serializers.AppUserSerializer
        return self.serializer_class


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'access',
                OpenApiTypes.STR,
                description='filter based on the Acess',
                enum=['is_superuser', 'is_staff'],
            ),
            OpenApiParameter(
                'gender',
                OpenApiTypes.STR,
                description='filter based on gender',
                enum=['Male', 'Female']
            )

        ]
    ),
)

class StaffViewSet(viewsets.ModelViewSet):
    """manage the staff API"""
    serializer_class = serializers.DetailDashboardUser
    queryset = get_user_model().objects.filter(Q(is_staff=True) | Q(is_superuser=True))
    filter_backends = (filters.SearchFilter,)
    search_fields=('email', 'first_name', 'last_name', 'phone_number', 'address')

    def get_serializer_class(self):
        """Return serializer class for the request"""
        if self.action == 'list':
            return serializers.DashboardUserSerializer
        return self.serializer_class

    def get_queryset(self):
        """filter the staff"""
        access = self.request.query_params.get('access')
        gender = self.request.query_params.get('gender')
        queryset = self.queryset

        if access:
            if access=='is_superuser':
                queryset = queryset.filter(is_superuser=True)
            else:
                queryset = queryset.filter(Q(is_staff=True) & Q(is_superuser=False))

        if gender:
            if gender == 'Male':
                queryset = queryset.filter(gender='Male')
            else:
                queryset = queryset.filter(gender='Female')

        return queryset.distinct().order_by('id')


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user"""
    serializer_class = serializers.DashboardTokenSerializer
    renderer_class = api_settings.DEFAULT_RENDERER_CLASSES

class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated User"""
    serializer_class = serializers.DetailDashboardUser
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Return and retrieve the authenticated User"""
        return self.request.user



@extend_schema_view(

    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'search',
                OpenApiTypes.STR,
                description='search'
            ),
        ]
    ),
)


class TeacherViewSet(viewsets.ModelViewSet):
    """manage the teacher API"""
    serializer_class = teacher_serializers.DetailDashboardTeacher
    queryset = teacher_models.Teacher.objects.all()
    filter_backends = (filters.SearchFilter,)
    search_fields=('email', 'first_name', 'last_name', 'phone_number', 'address')

    def get_serializer_class(self):
        """Return serializer class for the request"""
        if self.action == 'list':
            return teacher_serializers.TeacherSerializer
        return self.serializer_class



@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'search',
                OpenApiTypes.STR,
                description='search'
            ),
            OpenApiParameter(
                'price',
                OpenApiTypes.STR,
                description='Maximum price to filter',
            ),
            OpenApiParameter(
                'registration_open',
                OpenApiTypes.STR,
            description='registration_open',
            enum=[1,0]
            ),
            OpenApiParameter(
                'in_progress',
                OpenApiTypes.STR,
                description='in_progress',
                enum=[1,0]
            ),
        ]
    )
)

class CourseViewSet(viewsets.ModelViewSet):
    """manage  the course API"""
    serializer_class = course_serializers.DetailCourseSerializerv2
    queryset = course_models.Course.objects.all()
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', 'instructor__first_name', 'instructor__last_name', 'tags__name')


    def get_serializer_class(self):
        """return serializer class for the request"""
        if self.action == 'list':
            return course_serializers.CourseSerializer
        if self.action == 'add_student':
            return course_serializers.AddStudentToCourseSerializer
        if self.action == 'remove_student':
            return course_serializers.RemoveStudentFromCourseSerializer
        if self.action == 'create':
            return course_serializers.DetailCourseSerializer
        if self.action == 'end_course' or self.action == 'get_archive':
            return course_serializers.ArchiveSerializer
        if self.action == 'get_students':
            return course_serializers.CourseStudentSerializer
        if self.action == 'edit_student':
            return course_serializers.CourseStudentSerializer
        return self.serializer_class

    def create(self, request, *args, **kwargs):
        """rewriting the create method to use a different serializer
        for the response """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        serializer = course_serializers.DetailCourseSerializerv2(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """Override the default update method to use different
        serializer for the response"""

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        updated_instance = serializer.save()

        serializer = course_serializers.DetailCourseSerializerv2(updated_instance)
        return Response(serializer.data)

    def get_queryset(self):
        """filter the courses"""
        max_price = self.request.query_params.get('price')
        registration_open = self.request.query_params.get('registration_open')
        in_progress = self.request.query_params.get('in_progress')
        queryset = self.queryset
        if max_price:
          queryset = queryset.filter(price__lt=max_price)

        if in_progress:
            queryset = queryset.filter(in_progress=in_progress)

        if registration_open:
            queryset = queryset.filter(registration_open=registration_open)

        return queryset.distinct()

    @action(methods=['GET'], detail=True)
    def get_students(self, request, pk=None):
        """get the students registered in the course"""
        course = self.get_object()
        students = course.students.all()
        serializer = self.get_serializer(students, many=True)
        return Response(serializer.data)

    @action(methods=['PUT', 'PATCH'], detail=True)
    def edit_student(self, request, pk=None, *args, **kwargs):
        """get the students registered in the course"""
        course = self.get_object()
        partial = kwargs.get('partial', False)
        serializer = self.get_serializer(course, data=request.data, partial=partial, many=True)
        serializer.is_valid(raise_exception=True)
        instances = serializer.save()
        serializer = self.get_serializer(instances, many=True)
        return Response(serializer.data)

    @action(methods=['POST'], detail=False)
    def add_student(self, request, pk=None):
        """add a student to a course"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        course = serializer.save()
        serializer = course_serializers.DetailCourseSerializerv2(course)
        return Response(serializer.data)

    @action(methods=['POST'], detail=False)
    def remove_student(self, request, pk=None):
        """Remove a student from a course"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        course = serializer.save()
        serializer = course_serializers.DetailCourseSerializerv2(course)
        return Response(serializer.data)

    @action(methods=['POST'], detail=True)
    def end_course(self, request, pk=None):
        """End a course and
        save it to the archive"""

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        archive = serializer.save()
        return Response(serializer.data)

    @action(methods=['GET'], detail=True)
    def get_archive(self, request, pk=None):
        """Get the archive of the course"""
        queryset = course_models.Archive.objects.filter(course_id=pk)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)




class TagViewSet(mixins.ListModelMixin,
                 mixins.DestroyModelMixin,
                 mixins.UpdateModelMixin,
                 viewsets.GenericViewSet):
    """manage the tags """
    serializer_class = course_serializers.TagSerializer
    queryset = course_models.Tag.objects.all()



class ClassRoomViewSet(viewsets.ModelViewSet):
    """manage the classroom model"""
    serializer_class = schedule_serializers.ClassRoomSerializer
    queryset = schedule_models.ClassRoom.objects.all()


class CreateScheduleView(generics.CreateAPIView):
    """Create a shcedule instance"""
    serializer_class = schedule_serializers.ScheduleSerializer


class ScheduleViewset(mixins.ListModelMixin, viewsets.GenericViewSet):
    """get the serializer class"""
    serializer_class = schedule_serializers.ScheduleSerializer
    queryset = schedule_models.Schedule.objects.all()

    def get_serializer_class(self):
        """get the serializer for the
        request"""

        if self.action == 'add_to_schedule':
            return schedule_serializers.CourseTimeDaySerializer
        return self.serializer_class

    @action(methods=['POST'], detail=False)
    def add_to_schedule(self, request, *args, **kwargs):
        """add data to the schedule"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        serializer = schedule_serializers.CourseTimeSerializer(instance)
        return Response(serializer.data)

    @action(methods=['DELETE'], detail=True)
    def delete_from_schedule(self, request, pk):
        """delete data from the schedule"""
        try:
            course_time = schedule_models.CourseTime.objects.get(id=pk)
            course_time.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except schedule_models.CourseTime.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)




class CourseTimeViewset(viewsets.ModelViewSet):
    """manage the course times inside the schedule"""
    serializer_class = schedule_serializers.CourseTimeDaySerializer
    queryset = schedule_models.CourseTime.objects.all()

    def get_serializer_class(self):
        """get the serializer class based on the request method"""
        if self.action == 'create':
            return self.serializer_class
        elif self.action in ['update', 'partial_update']:
            return schedule_serializers.CourseTimeSerializerV2
        return schedule_serializers.CourseTimeSerializer

    def create(self, request, *args, **kwargs):
        """rewriting the create method to use a different serializer
        for the response """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        serializer = schedule_serializers.CourseTimeSerializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """Override the default update method to use different
        serializer for the response"""

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        updated_instance = serializer.save()

        serializer = schedule_serializers.CourseTimeSerializer(updated_instance)
        return Response(serializer.data)


class NotificationsViewSet(mixins.ListModelMixin,
                           viewsets.GenericViewSet):
    """View for listing notifications"""
    serializer_class = notification_serializers.NotificationSerializer
    queryset = notification_models.Notification.objects.all()

    def get_queryset(self):
        """make the newest notification appear
        ont top"""

        queryset = self.queryset
        queryset = queryset.order_by('-id')
        return queryset

    def get_serializer_class(self):
        """return serializer for the request"""
        if self.action == 'descision':
            return notification_serializers.DescisionSerializer
        return self.serializer_class

    @action(methods=['POST'], detail=False)
    def descision(self, request, *args, **kwargs):
        """process a descision and
        return feedback"""

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception= True)
        message = serializer.save()

        return Response({'message': message})
