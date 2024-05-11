from typing import TypeAlias, Any

import requests

from app.employees.models import Employee
from app.lessons.models import Lesson

IsCreated: TypeAlias = bool


class EmployeeSynker:
    def __init__(self):
        self.url = 'http://api:8080/api/employees'
        self.forbidden_words = ["инженер", "техник"]
        self.requester = requests
        self.employee_manager = Employee.objects
        self.lessons_manager = Lesson.objects

    def get_filtered_employees_data(self) -> list[dict[str, Any]]:
        employees_data = self.requester.get(self.url).json()
        return [
            employee_data
            for employee_data in employees_data
            if employee_data['post'] is None
            or not any(
                word in employee_data['post'].lower() for word in self.forbidden_words
            )
        ]

    def synk(self) -> None:
        self.employee_manager.all().delete()
        employees_data = self.requester.get(self.url).json()
        for employee_data in employees_data:
            name = self._parse_name(employee_data)
            self._update_or_create_employee(employee_data['id'], name)

    def synk_by_id(self, id: int) -> Employee:
        employees_data = self.get_filtered_employees_data()
        for employee_data in employees_data:
            if employee_data['id'] == id:
                name = self._parse_name(employee_data)
                is_created, employee = self._update_or_create_employee(id, name)
                if is_created:
                    self.lessons_manager.create_for_employee(employee)
                return employee
        raise KeyError

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
