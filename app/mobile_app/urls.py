"""
URL mapping for the mobile app API
"""

from django.urls import path, include
from mobile_app import views
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('tags', views.GetTagsViewSet)
router.register('courses', views.CoursesViewSet)
router.register('teachers', views.TeacherViewSet)
router.register('get-courses', views.StudentCoursesViewSet)
urlpatterns = [
    path('create-student/', views.CreateStudentView.as_view(), name='create-student'),
    path('token/', views.CreateTokenView.as_view(), name='token'),
    path('me/', views.ManageStudentView.as_view(), name='me'),
    path('', include(router.urls)),
    path('course-register/', views.CourseRegisterView.as_view(), name='course-register'),
]