from django.urls import path

from app.employees.views.delete_lessons import EmployeesDeleteLessonsView
from app.employees.views.general import EmployeesView

urlpatterns = [
    path('', EmployeesView.as_view()),
    path('delete_lessons/', EmployeesDeleteLessonsView.as_view())
]
