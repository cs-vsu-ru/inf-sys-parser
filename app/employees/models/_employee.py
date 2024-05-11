from django.db import models

from app.base.models.base import BaseModel


class Employee(BaseModel):
    id = models.BigIntegerField(primary_key=True)
    name = models.TextField(db_index=True)
