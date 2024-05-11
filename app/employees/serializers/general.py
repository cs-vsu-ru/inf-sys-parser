from rest_framework import serializers

from app.base.exceptions import APIWarning
from app.base.serializers.base import BaseSerializer


class POST_EmployeesSerializer(BaseSerializer):
    WARNINGS = {
        404: APIWarning(
            "Employee with this `id` was not found on `/api/employees/`",
            404,
            'employee_not_found_by_id',
        )
    }

    employee_id = serializers.IntegerField(write_only=True)
