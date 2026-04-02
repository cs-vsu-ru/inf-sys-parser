from django.urls import path

from app.students.views.parse import StudentsImportView

urlpatterns = [
    path('import/', StudentsImportView.as_view()),
]
