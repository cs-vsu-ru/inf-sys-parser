from django.urls import path

from app.lessons.views import (
    LessonsParseView,
    LessonsView,
    LessonsByEmployeeView,
    LessonView,
    LessonsByEmployeeXlsxView,
    LessonsXlsxView,
)

urlpatterns = [
    path('', LessonsView.as_view()),
    path('xlsx/', LessonsXlsxView.as_view()),
    path('<int:id>/', LessonView.as_view()),
    path('by_employee/<int:employee_id>/', LessonsByEmployeeView.as_view()),
    path('by_employee/<int:employee_id>/xlsx/', LessonsByEmployeeXlsxView.as_view()),
    path('parse/', LessonsParseView.as_view()),
]
