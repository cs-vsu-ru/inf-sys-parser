from django.db import models

from app.base.models.base import BaseModel


class Student(BaseModel):
    ACTIVITY_STUDENT = 'student'
    ACTIVITY_MASTER = 'master'
    ACTIVITY_PHD = 'phd'

    ACTIVITY_CHOICES = [
        (ACTIVITY_STUDENT, 'студент'),
        (ACTIVITY_MASTER, 'магистрант'),
        (ACTIVITY_PHD, 'аспирант'),
    ]

    full_name = models.TextField(db_index=True)
    login = models.TextField(unique=True, db_index=True)
    email = models.EmailField()
    course = models.PositiveSmallIntegerField()
    group = models.TextField(db_index=True)
    subgroup = models.TextField()
    education_profile = models.TextField()
    activity_type = models.TextField(
        choices=ACTIVITY_CHOICES,
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ['login']