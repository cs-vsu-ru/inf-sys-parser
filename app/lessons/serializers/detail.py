from app.base.serializers.base import BaseModelSerializer
from app.lessons.models import Lesson


class PATCH_LessonSerializer(BaseModelSerializer):
    class Meta:
        model = Lesson
        write_only_fields = ['name', 'groups', 'placement']
