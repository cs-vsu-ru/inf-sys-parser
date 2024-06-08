from app.base.utils.common import response_204

from app.base.views.base import BaseView
from app.employees.services.synker import EmployeeSynker
from app.lessons.models import Lesson
from app.lessons.serializers.parse import POST_LessonsParseSerializer
from app.lessons.services.parser import Parser


class LessonsParseView(BaseView):
    FILENAME = 'schedule.xlsx'
    serializer_map = {'post': POST_LessonsParseSerializer}

    @response_204
    def post(self):
        self.process()
        self.process()

    def process(self):
        employee_synker = EmployeeSynker()
        parser = Parser()
        self._upload_file()
        lessons = parser.parse(self.FILENAME)
        employee_synker.synk()
        Lesson.objects.create_for_all_employees(lessons)

    def _upload_file(self):
        serializer = self.get_valid_serializer()
        file = serializer.validated_data['file']
        file_path = self.FILENAME
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
