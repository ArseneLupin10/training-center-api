"""
URL mappings for the dashboard API
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from dashboard import views


router = DefaultRouter()
router.register('students', views.StudentViewSet)
router.register('staff', views.StaffViewSet)
router.register('teachers', views.TeacherViewSet)
router.register('courses', views.CourseViewSet)
router.register('tags', views.TagViewSet)
router.register('classroom', views.ClassRoomViewSet)
router.register('schedule-data', views.CourseTimeViewset)
router.register('schedule', views.ScheduleViewset)
router.register('notification', views.NotificationsViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('token/', views.CreateTokenView.as_view(), name='token'),
    path('me/', views.ManageUserView.as_view(), name='me'),
    path('schedules/create/', views.CreateScheduleView.as_view(), name='schedule'),
]