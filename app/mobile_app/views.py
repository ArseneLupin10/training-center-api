"""
Views for the mobile app
"""

from rest_framework import(
    generics,
    authentication,
    permissions,
    mixins,
    viewsets,
    filters,
)
from rest_framework.response import Response
from user.serializers import AppUserSerializer, AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from core.permissions import IsStudent
from course import serializers as CourseSerializers
from course import models as CourseModels
from teacher import(
     serializers as TeacherSerializers,
     models as TeacherModels,
)
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.exceptions import PermissionDenied


class CreateStudentView(generics.CreateAPIView):
    """Create a new student"""
    serializer_class = AppUserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user"""
    serializer_class = AuthTokenSerializer
    renderer_class = api_settings.DEFAULT_RENDERER_CLASSES



class ManageStudentView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated student"""
    serializer_class = AppUserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsStudent, permissions.IsAuthenticated]

    def get_object(self):
        """Return and retrieve the authenticated student"""
        return self.request.user


class GetTagsViewSet(mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    """list all the Tags """

    serializer_class = CourseSerializers.TagSerializer
    queryset = CourseModels.Tag.objects.all()


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
                'level',
                OpenApiTypes.STR,
                description='level to filter',
                enum = [
                    'all_levels',
                    'beginner',
                    'intermediate',
                    'expert',
                ]
            )
        ]
    )
)


class CoursesViewSet(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    """Retreive and list courses """
    serializer_class = CourseSerializers.MobileAppDetailCourseSerializer
    queryset = CourseModels.Course.objects.all()
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', 'instructor__first_name', 'instructor__last_name', 'tags__name')
    authentication_classes = [authentication.TokenAuthentication]

    def get_serializer_class(self):
        """return serializer class for the request"""
        if self.action == 'list':
            return CourseSerializers.MobileAppCourseSerializer
        if self.action == 'post_comment':
            return CourseSerializers.PostCommentSerializer
        return self.serializer_class

    def get_queryset(self):
        """filter the courses"""
        max_price = self.request.query_params.get('price')
        level = self.request.query_params.get('level')
        queryset = self.queryset
        if max_price:
          queryset = queryset.filter(price__lt=max_price)

        if level:
            queryset = queryset.filter(level=level)

        return queryset.distinct().order_by('-rating')


    def get_permissions(self):
        """return the permissions
        required for the action """
        if self.action == 'post_comment' or self.action == 'delete_comment':
            return [permissions.IsAuthenticated(), IsStudent()]
        return []

    @action(methods=['POST'], detail=True)
    def post_comment(self, request, pk=None):
        """post a comment to the course"""
        course = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(student=request.user, course=course)
        return Response(serializer.data)

    @action(detail=True, methods=['DELETE'], url_path='comments/(?P<comment_id>\d+)')
    def delete_comment(self, request, pk=None, comment_id=None):
        try:
            course = self.get_object()  # Get the course object
            comment = course.comments.get(id=comment_id)  # Get the comment object
            if comment.student != request.user:
                raise PermissionDenied("You don't have permission to delete this comment.")
            comment.delete()  # Delete the comment
            return Response(status=status.HTTP_204_NO_CONTENT)
        except comment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class TeacherViewSet(mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    """manage the teacher API """
    serializer_class = TeacherSerializers.DetailAppTeacher
    queryset = TeacherModels.Teacher.objects.all()


class CourseRegisterView(generics.CreateAPIView):
    """register students to courses"""
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsStudent, permissions.IsAuthenticated]
    serializer_class = CourseSerializers.RegisterSerializer

    def create(self, request, *args, **kwargs):
        """alter the create method"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        student = serializer.save()
        courses = CourseModels.Course.objects.filter(students__student=student)
        serializer = CourseSerializers.CourseSerializer(courses, many=True)
        return Response(serializer.data)


class StudentCoursesViewSet(mixins.ListModelMixin,
                            viewsets.GenericViewSet):
    """list the courses of the authorized student"""
    serializer_class = CourseSerializers.CourseSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsStudent, permissions.IsAuthenticated]
    queryset = CourseModels.Course.objects.all()

    def get_queryset(self):
        """filter the courses"""
        queryset = self.queryset
        student = self.request.user
        return queryset.filter(students__student=student)


class CommentViewSet(mixins.CreateModelMixin,
                     viewsets.GenericViewSet):
    """viewset for the comment API"""
    serializer_classes = CourseSerializers.PostCommentSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsStudent, permissions.IsAuthenticated]
    queryset = CourseModels.Comment.objects.all()



