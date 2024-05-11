from rest_framework import serializers
from typing import Any

from app.base.serializers.base import BaseModelSerializer, BaseSerializer
from app.employees.models import Employee
from app.lessons.models import Lesson


class _GET_LessonsByEmployee_Schedule_LessonSerializer(BaseModelSerializer):
    class Meta:
        model = Lesson
        read_only_fields = ['id', 'name', 'groups', 'placement']


class _GET_LessonsByEmployee_ScheduleSerializer(BaseSerializer):
    time = serializers.CharField()
    monday = _GET_LessonsByEmployee_Schedule_LessonSerializer(many=True)
    tuesday = _GET_LessonsByEmployee_Schedule_LessonSerializer(many=True)
    wednesday = _GET_LessonsByEmployee_Schedule_LessonSerializer(many=True)
    thursday = _GET_LessonsByEmployee_Schedule_LessonSerializer(many=True)
    friday = _GET_LessonsByEmployee_Schedule_LessonSerializer(many=True)
    saturday = _GET_LessonsByEmployee_Schedule_LessonSerializer(many=True)


class GET_LessonsByEmployeeSerializer(BaseModelSerializer):
    schedule = _GET_LessonsByEmployee_ScheduleSerializer(many=True)

    class Meta:
        model = Employee
        read_only_fields = ['id', 'name', 'schedule']

    TIMES = [
        '8:00 - 9:35',
        '9:45 - 11:20',
        '11:30 - 13:05',
        '13:25 - 15:00',
        '15:10 - 16:45',
        '16:55 - 18:30',
        '18:40 - 20:00',
        '20:10 - 21:30',
    ]
    WEEKDAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']

    def to_representation(self, instance: Employee):
        instance.schedule = self._get_schedule()
        return super().to_representation(instance)

    def _get_schedule(self) -> list[dict[str, Any]]:
        employee = self.instance
        lessons = Lesson.objects.index_lessons(Lesson.objects.filter(employee=employee))
        schedule = []
        for number, time_name in enumerate(self.TIMES):
            schedule_by_number = {'time': time_name}
            for weekday, weekday_name in enumerate(self.WEEKDAYS):
                lessons_by_weekday = []
                for is_denominator in False, True:
                    lesson = lessons[(employee, weekday, number, is_denominator)]
                    lessons_by_weekday.append(lesson)
                schedule_by_number[weekday_name] = lessons_by_weekday
            schedule.append(schedule_by_number)
        return schedule
