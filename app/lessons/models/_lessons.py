from django.db import models

from app.base.models.base import BaseModel
from app.employees.models import Employee
from app.lessons.managers.lesson import LessonManager


class Lesson(BaseModel):
    employee = models.ForeignKey(Employee, models.CASCADE, related_name='lessons')
    weekday = models.SmallIntegerField(db_index=True)
    number = models.SmallIntegerField(db_index=True)
    is_denominator = models.BooleanField()
    name = models.TextField(blank=True)
    groups = models.TextField(blank=True)
    placement = models.TextField(blank=True)

    objects = LessonManager()
