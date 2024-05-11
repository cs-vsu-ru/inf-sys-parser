from django.http import FileResponse, HttpResponse

from app.base.views.base import BaseView
from app.employees.models import Employee
from app.lessons.services.xlsx.builders.employee_schedule import (
    XlsxEmployeeScheduleBuilder,
)


class LessonsByEmployeeXlsxView(BaseView):
    queryset = Employee.objects.all()
    lookup_field = 'id'
    lookup_url_kwarg = 'employee_id'

    CONTENT_TYPE = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    def get(self):
        employee: Employee = self.get_object()
        builder = XlsxEmployeeScheduleBuilder(employee)
        filename = builder.build()
        return self._get_response(filename)

    def _get_response(self, filename: str) -> HttpResponse:
        with open(filename, 'rb') as file:
            response = HttpResponse(file, content_type=self.CONTENT_TYPE)
            response['Content-Disposition'] = f"attachment; filename={filename}"
            return response
