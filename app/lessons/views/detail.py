from app.base.utils.common import response_204

from app.base.views.base import BaseView
from app.lessons.models import Lesson
from app.lessons.serializers.detail import PATCH_LessonSerializer


class LessonView(BaseView):
    serializer_map = {'patch': PATCH_LessonSerializer}
    queryset = Lesson.objects.all()

    @response_204
    def patch(self):
        self.update()
