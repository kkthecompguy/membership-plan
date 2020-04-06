from django.urls import path
from .views import CourseDetailView, CourseListView, LessonDetailView

app_name = 'courses'
urlpatterns = [
  path('', CourseListView.as_view(), name='list'),
  path('courses/<str:slug>/', CourseDetailView.as_view(), name='detail'),
  path('courses/<str:course_slug>/<str:lesson_slug>/', LessonDetailView.as_view(), name='lesson-detail'),
]