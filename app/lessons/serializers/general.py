from rest_framework import serializers

from app.base.serializers.base import BaseModelSerializer, BaseSerializer
from app.employees.models import Employee
from app.lessons.models import Lesson


class _GET_Lessons_Schedule_Times_LessonSerializer(BaseModelSerializer):
    class Meta:
        model = Lesson
        read_only_fields = ['id', 'name', 'groups', 'placement']


class _GET_Lessons_Schedule_TimeSerializer(BaseSerializer):
    time = serializers.CharField()
    lessons = serializers.ListSerializer(
        child=_GET_Lessons_Schedule_Times_LessonSerializer(many=True)
    )


class _GET_Lessons_ScheduleSerializer(BaseSerializer):
    weekday = serializers.CharField()
    times = _GET_Lessons_Schedule_TimeSerializer(many=True)


class _GET_Lessons_EmployeesSerializer(BaseModelSerializer):
    class Meta:
        model = Employee
        read_only_fields = ['id', 'name']


class GET_LessonsSerializer(BaseSerializer):
    employees = _GET_Lessons_EmployeesSerializer(many=True)
    schedule = _GET_Lessons_ScheduleSerializer(many=True)

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
    WEEKDAYS = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']

    def to_representation(self, instance):
        instance['schedule'] = self._get_schedule()
        return super().to_representation(instance)

    def _get_schedule(
        self,
    ) -> list[dict[str | list[dict[str, str | list[list[Lesson]]]]]]:
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
                schedule_by_number = {'time': time_name, 'lessons': lessons_by_number}
                times_by_weekday.append(schedule_by_number)
            schedule_by_weekday = {'weekday': weekday_name, 'times': times_by_weekday}
            schedule.append(schedule_by_weekday)
        return schedule
