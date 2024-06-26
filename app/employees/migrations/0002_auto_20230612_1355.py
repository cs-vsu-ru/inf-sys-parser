# Generated by Django 4.2.1 on 2023-06-12 13:55
import time

from django.db import migrations

from app.employees.services.synker import EmployeeSynker


def delete_filtered_employees(apps, _):
    Employee = apps.get_model('employees', 'Employee')
    Lesson = apps.get_model('lessons', 'Lesson')
    synker = EmployeeSynker()
    synker.employee_manager = Employee.objects
    synker.lessons_manager = Lesson.objects
    try_count = 0
    while True:
        try:
            filtered_employees_data = synker.get_filtered_employees_data()
            break
        except Exception as exc:
            if try_count > 4:
                raise RuntimeError(
                    "Не получилось получить filtered_employees_data во время миграции"
                ) from exc
            time.sleep(10)
            try_count += 1
    synker.employee_manager.exclude(
        id__in=[data['id'] for data in filtered_employees_data]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0001_initial'),
        ('lessons', '0001_initial')
    ]

    operations = [migrations.RunPython(delete_filtered_employees)]
