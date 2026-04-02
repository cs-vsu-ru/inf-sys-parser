from rest_framework import serializers
from app.base.serializers.base import BaseSerializer


class POST_StudentsImportSerializer(BaseSerializer):
    file = serializers.FileField(write_only=True)

    def validate_file(self, file):
        if not file.name.endswith('.xlsx'):
            raise serializers.ValidationError(
                'Поддерживается только формат .xlsx'
            )
        return file


class StudentsImportErrorSerializer(serializers.Serializer):
    row = serializers.IntegerField()
    field = serializers.CharField()
    message = serializers.CharField()


class POST_StudentsImportResponseSerializer(BaseSerializer):
    created = serializers.IntegerField(read_only=True)
    updated = serializers.IntegerField(read_only=True)
    errors = StudentsImportErrorSerializer(many=True, read_only=True)
