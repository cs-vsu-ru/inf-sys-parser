from datetime import timedelta

from django.db import models

from app.base.models.base import BaseModel
from app.base.utils.common import moscow_today


class WeekConfig(BaseModel):
    reference_date = models.DateField()
    is_denominator = models.BooleanField()

    class Meta(BaseModel.Meta):
        verbose_name = 'week config'

    def get_current_is_denominator(self) -> bool:
        today = moscow_today()
        current_monday = today - timedelta(days=today.weekday())
        ref_monday = self.reference_date - timedelta(days=self.reference_date.weekday())
        weeks_elapsed = (current_monday - ref_monday).days // 7
        if weeks_elapsed % 2 == 0:
            return self.is_denominator
        return not self.is_denominator
