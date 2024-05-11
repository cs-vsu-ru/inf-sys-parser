from django.http import HttpResponse

from app.base.views.base import BaseView
from app.lessons.services.xlsx.builders.employees_schedule import (
    XlsxEmployeesScheduleBuilder,
)


class LessonsXlsxView(BaseView):
    CONTENT_TYPE = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    def get(self):
        builder = XlsxEmployeesScheduleBuilder()
        filename = builder.build()
        return self._get_response(filename)

    def _get_response(self, filename: str) -> HttpResponse:
        with open(filename, 'rb') as file:
            response = HttpResponse(file, content_type=self.CONTENT_TYPE)
            response['Content-Disposition'] = f"attachment; filename={filename}"
            return response
