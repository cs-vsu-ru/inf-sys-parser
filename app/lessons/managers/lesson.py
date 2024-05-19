from __future__ import annotations

from typing import TypeAlias

from django.db.models import Manager

import app.lessons.models
from app.employees.models import Employee

Lesson: TypeAlias = 'app.lessons.models.Lesson'
Weekday: TypeAlias = int
Number: TypeAlias = int


class LessonManager(Manager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.employee_manager = Employee.objects

    def create_for_all_employees(self, lessons: list[Lesson]) -> None:
        lessons_to_create = []
        indexed_lessons = self.index_lessons(lessons)
        for employee in self.employee_manager.all():
            for weekday in range(6):
                for number in range(8):
                    for is_denominator in False, True:
                        lesson = indexed_lessons.get(
                            (employee, weekday, number, is_denominator),
                            self.model(
                                employee=employee,
                                weekday=weekday,
                                number=number,
                                is_denominator=is_denominator,
                                name='',
                                groups='',
                                placement='',
                            ),
                        )
                        lessons_to_create.append(lesson)
        self.all().delete()
        self.bulk_create(lessons_to_create)

    def create_for_employee(self, employee: Employee) -> None:
        lessons_to_create = []
        for weekday in range(6):
            for number in range(8):
                for is_denominator in False, True:
                    lesson = self.model(
                        employee=employee,
                        weekday=weekday,
                        number=number,
                        is_denominator=is_denominator,
                        name='',
                        groups='',
                        placement='',
                    )
                    lessons_to_create.append(lesson)
        self.bulk_create(lessons_to_create)

    def delete_for_employee(self, employee: Employee) -> None:
        self.filter(employee=employee).delete()

    def index_lessons(
        self, lessons: list
    ) -> dict[tuple[Employee, Weekday, Number, bool], Lesson]:
        indexed_lessons = {}
        for lesson in lessons:
            indexed_lessons[
                (lesson.employee, lesson.weekday, lesson.number, lesson.is_denominator)
            ] = lesson
        return indexed_lessons
