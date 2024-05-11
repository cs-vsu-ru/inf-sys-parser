from django.core.cache import cache
from rest_framework.response import Response

from app.base.views.base import BaseView
from app.employees.models import Employee
from app.lessons.serializers.general import GET_LessonsSerializer


class LessonsView(BaseView):
    serializer_map = {'get': GET_LessonsSerializer}
    queryset = Employee.objects.order_by('name')
    pagination_class = None

    def get(self):
        if (data := cache.get('lessons')) is None:
            serializer = self.get_serializer(
                {'employees': self.get_filtered_queryset()}
            )
            data = serializer.data
            cache.set('lessons', data, 1)
        return Response(data)
