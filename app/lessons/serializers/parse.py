from rest_framework import serializers

from app.base.serializers.base import BaseModelSerializer
from app.lessons.models import Lesson


class POST_LessonsParseSerializer(BaseModelSerializer):
    file = serializers.FileField()
    
    class Meta:
        model = Lesson
        write_only_fields = ['file']
