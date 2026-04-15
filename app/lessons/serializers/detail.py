from rest_framework import serializers

from app.base.serializers.base import BaseModelSerializer
from app.lessons.models import Lesson


class PATCH_LessonSerializer(BaseModelSerializer):
    WEEK_TYPE_EVERY = 'EVERY'
    WEEK_TYPE_NUMERATOR = 'NUMERATOR'
    WEEK_TYPE_DENOMINATOR = 'DENOMINATOR'

    week_type = serializers.ChoiceField(
        choices=(
            (WEEK_TYPE_EVERY, 'Каждую неделю'),
            (WEEK_TYPE_NUMERATOR, 'Числитель'),
            (WEEK_TYPE_DENOMINATOR, 'Знаменатель'),
        ),
        required=False,
        write_only=True,
    )

    class Meta:
        model = Lesson
        write_only_fields = ['name', 'groups', 'placement', 'week_type']

    def update(self, instance, validated_data):
        week_type = validated_data.pop('week_type', None)

        if week_type == self.WEEK_TYPE_EVERY:
            lessons_to_update = Lesson.objects.filter(
                employee=instance.employee,
                weekday=instance.weekday,
                number=instance.number,
            )

        elif week_type == self.WEEK_TYPE_NUMERATOR:
            lessons_to_update = Lesson.objects.filter(
                employee=instance.employee,
                weekday=instance.weekday,
                number=instance.number,
                is_denominator=False,
            )

        elif week_type == self.WEEK_TYPE_DENOMINATOR:
            lessons_to_update = Lesson.objects.filter(
                employee=instance.employee,
                weekday=instance.weekday,
                number=instance.number,
                is_denominator=True,
            )

        else:
            lessons_to_update = Lesson.objects.filter(id=instance.id)

        fields = list(validated_data.keys())

        for lesson in lessons_to_update:
            for field, value in validated_data.items():
                setattr(lesson, field, value)
            lesson.save(update_fields=fields)

        if week_type == self.WEEK_TYPE_NUMERATOR:
            return Lesson.objects.get(
                employee=instance.employee,
                weekday=instance.weekday,
                number=instance.number,
                is_denominator=False,
            )

        if week_type == self.WEEK_TYPE_DENOMINATOR:
            return Lesson.objects.get(
                employee=instance.employee,
                weekday=instance.weekday,
                number=instance.number,
                is_denominator=True,
            )

        return instance
