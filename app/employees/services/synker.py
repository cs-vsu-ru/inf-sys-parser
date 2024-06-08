import os
from typing import TypeAlias, Any

import requests

from app.employees.models import Employee
from app.lessons.models import Lesson

IsCreated: TypeAlias = bool


class EmployeeSynker:
    def __init__(self):
        self.url = os.getenv('SERVER_URL') + 'api/employees'
        self.requester = requests
        self.employee_manager = Employee.objects
        self.lessons_manager = Lesson.objects

    def get_filtered_employees_data(self) -> list[dict[str, Any]]:
        employees_data = self.requester.get(self.url).json()
        return [
            employee_data
            for employee_data in employees_data
            if employee_data['hasLessons'] is True
        ]

    def synk(self) -> None:
        self.employee_manager.all().delete()
        employees_data = self.get_filtered_employees_data()
        for employee_data in employees_data:
            name = self._parse_name(employee_data)
            self._update_or_create_employee(employee_data['id'], name)

    def synk_by_id(self, id: int) -> Employee:
        employee_data = self.requester.get(self.url + f'/{id}').json()
        name = self._parse_name(employee_data)
        is_created, employee = self._update_or_create_employee(id, name)
        if is_created:
            self.lessons_manager.create_for_employee(employee)
        return employee

    def _update_or_create_employee(
            self, id: int, name: str
    ) -> tuple[IsCreated, Employee]:
        try:
            employee = self.employee_manager.get(id=id)
            employee.name = name
            employee.save()
            return False, employee
        except self.employee_manager.model.DoesNotExist:
            employee = self.employee_manager.create(id=id, name=name)
            return True, employee

    def _parse_name(self, employee_data) -> str:
        first_name = employee_data['firstName']
        last_name = employee_data['lastName']
        patronymic = employee_data['patronymic']
        return f"{last_name} {first_name[0]}.{patronymic[0]}."

    def delete_lessons_by_id(self, id: int):
        employee_to_delete = self.employee_manager.get(id=id)
        self.lessons_manager.delete_for_employee(employee_to_delete)
        employee_to_delete.delete()
    raise KeyError
