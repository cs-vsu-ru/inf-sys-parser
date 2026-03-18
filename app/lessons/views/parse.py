from app.base.views.base import BaseView
from app.employees.services.synker import EmployeeSynker
from app.lessons.models import Lesson
from app.lessons.serializers.parse import POST_LessonsParseSerializer
from app.lessons.services.parser import Parser
from rest_framework.response import Response


class LessonsParseView(BaseView):
    FILENAME = 'schedule.xlsx'
    serializer_map = {'post': POST_LessonsParseSerializer}

    def post(self):
        errors = self.process()
        return Response({'errors': errors})

    def process(self):
        employee_synker = EmployeeSynker()
        parser = Parser()
        self._upload_file()
        lessons = parser.parse(self.FILENAME)
        employee_synker.synk()
        Lesson.objects.create_for_all_employees(lessons)
        return parser.errors

    def _upload_file(self):
        serializer = self.get_valid_serializer()
        file = serializer.validated_data['file']
        file_path = self.FILENAME
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
