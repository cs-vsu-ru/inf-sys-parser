from rest_framework import status
from rest_framework.response import Response

from app.base.views.base import BaseView
from app.students.serializers.general import (
    POST_StudentsImportResponseSerializer,
    POST_StudentsImportSerializer,
)
from app.students.services.importer import StudentsXlsxImporter


class StudentsImportView(BaseView):
    serializer_map = {
        'post': (status.HTTP_200_OK, POST_StudentsImportResponseSerializer),
    }

    def post(self):
        serializer = self.get_valid_serializer(
            data=self.get_data()
        )
        file = serializer.validated_data['file']

        importer = StudentsXlsxImporter()
        result = importer.import_file(file)

        response_status = status.HTTP_200_OK
        if result.created == 0 and result.updated == 0 and result.errors:
            response_status = status.HTTP_400_BAD_REQUEST

        return Response(
            {
                'created': result.created,
                'updated': result.updated,
                'errors': result.errors,
            },
            status=response_status,
        )

    def get_serializer_class(self):
        if self.method == 'post':
            return POST_StudentsImportSerializer
        return super().get_serializer_class()
