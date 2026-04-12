from datetime import datetime, time

from rest_framework import serializers

from app.base.serializers.base import BaseModelSerializer, BaseSerializer
from app.employees.models import Employee
from app.lessons.models import Lesson, WeekConfig


class _GET_Lessons_Schedule_Times_LessonSerializer(BaseModelSerializer):
    class Meta:
        model = Lesson
        read_only_fields = ['id', 'name', 'groups', 'placement']


class _GET_Lessons_Schedule_TimeSerializer(BaseSerializer):
    time = serializers.CharField()
    is_current = serializers.BooleanField()
    lessons = serializers.ListSerializer(
        child=_GET_Lessons_Schedule_Times_LessonSerializer(many=True)
    )


class _GET_Lessons_ScheduleSerializer(BaseSerializer):
    weekday = serializers.CharField()
    is_current = serializers.BooleanField()
    times = _GET_Lessons_Schedule_TimeSerializer(many=True)


class _GET_Lessons_EmployeesSerializer(BaseModelSerializer):
    class Meta:
        model = Employee
        read_only_fields = ['id', 'name']


class GET_LessonsSerializer(BaseSerializer):
    employees = _GET_Lessons_EmployeesSerializer(many=True)
    schedule = _GET_Lessons_ScheduleSerializer(many=True)
    is_denominator = serializers.BooleanField()

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
    TIME_RANGES = [
        (time(8, 0), time(9, 35)),
        (time(9, 45), time(11, 20)),
        (time(11, 30), time(13, 5)),
        (time(13, 25), time(15, 0)),
        (time(15, 10), time(16, 45)),
        (time(16, 55), time(18, 30)),
        (time(18, 40), time(20, 0)),
        (time(20, 10), time(21, 30)),
    ]
    WEEKDAYS = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']

    def to_representation(self, instance):
        now = datetime.now()
        current_weekday = now.weekday()  # 0=Mon … 5=Sat, 6=Sun
        current_time = now.time()

        current_slot = None
        for i, (start, end) in enumerate(self.TIME_RANGES):
            if start <= current_time <= end:
                current_slot = i
                break

        config = WeekConfig.objects.first()
        if config is not None:
            is_denominator = config.get_current_is_denominator()
        else:
            is_denominator = now.isocalendar()[1] % 2 == 0

        instance['schedule'] = self._get_schedule(current_weekday, current_slot)
        instance['is_denominator'] = is_denominator
        return super().to_representation(instance)

    def _get_schedule(self, current_weekday: int, current_slot: int | None) -> list:
        employees: list[Employee] = self.instance['employees']
        lessons = Lesson.objects.index_lessons(Lesson.objects.all())
        schedule = []
        for weekday, weekday_name in enumerate(self.WEEKDAYS):
            times_by_weekday = []
            for number, time_name in enumerate(self.TIMES):
                lessons_by_number = []
                for employee in employees:
                    lessons_by_employee = []
                    for is_denominator in False, True:
                        lesson = lessons[(employee, weekday, number, is_denominator)]
                        lessons_by_employee.append(lesson)
                    lessons_by_number.append(lessons_by_employee)
                times_by_weekday.append({
                    'time': time_name,
                    'is_current': number == current_slot,
                    'lessons': lessons_by_number,
                })
            schedule.append({
                'weekday': weekday_name,
                'is_current': weekday == current_weekday,
                'times': times_by_weekday,
            })
        return schedule
