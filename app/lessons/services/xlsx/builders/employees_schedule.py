from copy import copy
from typing import TypeAlias

from openpyxl import load_workbook

from app.employees.models import Employee
from app.lessons.models import Lesson

TargetFilename: TypeAlias = str


class XlsxEmployeesScheduleBuilder:
    def __init__(self):
        self.template_filename = 'employees_schedule_template.xlsx'
        self.target_filename = 'employees_schedule.xlsx'
        self.lesson_manager = Lesson.objects
        self.employees_manager = Employee.objects

    def build(self) -> TargetFilename:
        employees = list(self.employees_manager.order_by('name'))
        lessons = self.lesson_manager.index_lessons(self.lesson_manager.all())
        wb = load_workbook(self.template_filename)
        ws = wb.active
        # Row 1: columns 0–1 are fixed; teacher names start at 0-based index 2 (Excel column C).
        template_right_col = ws.max_column
        max_slots = max(0, template_right_col - 2)
        extra = len(employees) - max_slots
        if extra > 0:
            # Template width is fixed; append columns so every employee gets a slot (avoids IndexError).
            ws.insert_cols(template_right_col + 1, extra)
        for index, employee in enumerate(employees):
            # 0-based offset in row tuples; Excel column index is 1-based (use cell(), not ws[row][i] —
            # after insert_cols, row tuples may still be too short and raise IndexError).
            column = index + 2
            col_1based = column + 1
            ws.cell(row=1, column=col_1based).value = employee.name
            for weekday in range(6):
                for number in range(8):
                    numerator_row = self._get_numerator_row(weekday, number)
                    denominator_row = numerator_row + 1
                    numerator_lesson = lessons[(employee, weekday, number, False)]
                    denominator_lesson = lessons[(employee, weekday, number, True)]
                    ws.cell(row=numerator_row, column=col_1based).value = (
                        self._get_cell(numerator_lesson)
                    )
                    ws.cell(row=denominator_row, column=col_1based).value = (
                        self._get_cell(denominator_lesson)
                    )
                    if self._check_merge(numerator_lesson, denominator_lesson):
                        ws.merge_cells(
                            start_row=numerator_row,
                            start_column=col_1based,
                            end_row=denominator_row,
                            end_column=col_1based,
                        )
        if extra > 0:
            # insert_cols adds blank cells without the template border; mirror last template column.
            max_r = self._get_numerator_row(5, 7) + 1
            for col in range(template_right_col + 1, template_right_col + extra + 1):
                for row in range(1, max_r + 1):
                    src = ws.cell(row=row, column=template_right_col)
                    dst = ws.cell(row=row, column=col)
                    dst.border = copy(src.border)
        wb.save(self.target_filename)
        return self.target_filename

    def _get_numerator_row(self, weekday: int, number: int) -> int:
        return weekday * 16 + number * 2 + 2

    def _get_cell(self, lesson: Lesson) -> str:
        return f"{lesson.name} {lesson.groups} {lesson.placement}"

    def _check_merge(
        self, numerator_lesson: Lesson, denominator_lesson: Lesson
    ) -> bool:
        return (
            numerator_lesson.name == denominator_lesson.name
            and numerator_lesson.groups == denominator_lesson.groups
            and numerator_lesson.placement == denominator_lesson.placement
        )
