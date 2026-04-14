from datetime import timedelta

from django.core.cache import cache
from rest_framework.response import Response

from app.base.utils.common import moscow_today
from app.base.views.base import BaseView
from app.lessons.models import WeekConfig
from app.lessons.serializers.week_config import GET_WeekConfigSerializer, PATCH_WeekConfigSerializer


class WeekConfigView(BaseView):
    serializer_map = {
        'get': GET_WeekConfigSerializer,
        'patch': PATCH_WeekConfigSerializer,
    }

    def _get_or_default(self) -> WeekConfig:
        config = WeekConfig.objects.first()
        if config is None:
            today = moscow_today()
            config = WeekConfig(
                reference_date=today - timedelta(days=today.weekday()),
                is_denominator=today.isocalendar()[1] % 2 == 0,
            )
        return config

    def get(self):
        return Response(self.get_serializer(self._get_or_default()).data)

    def patch(self):
        config = WeekConfig.objects.first()
        partial = config is not None
        serializer = self.get_valid_serializer(config, data=self.request.data, partial=partial)
        serializer.save()
        cache.delete('lessons')
        return Response(serializer.data)
