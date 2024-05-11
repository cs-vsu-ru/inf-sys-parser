from django.http import Http404

from app.base.views.base import BaseView
from app.employees.models import Employee
from app.employees.services.synker import EmployeeSynker
from app.lessons.serializers.by_employee.general import GET_LessonsByEmployeeSerializer


class LessonsByEmployeeView(BaseView):
    serializer_map = {'get': GET_LessonsByEmployeeSerializer}
    queryset = Employee.objects.all()
    lookup_field = 'id'
    lookup_url_kwarg = 'employee_id'

    def get(self):
        return self.retrieve()

    def get_object(self) -> Employee:
        try:
            return super().get_object()
        except Http404 as exc404:
            synker = EmployeeSynker()
            id = self.kwargs[self.lookup_url_kwarg]
            try:
                return synker.synk_by_id(id)
            except KeyError as exc:
                raise exc404 from exc
