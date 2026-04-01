from copy import copy
from typing import TypeAlias

from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font

from app.employees.models import Employee
from app.lessons.models import Lesson

TargetFilename: TypeAlias = str

_COLS_PER_TEACHER = 2
_FIXED_LEFT_COLS = 2

_HEADER_FONT = Font(bold=True, size=12)
_CELL_ALIGNMENT = Alignment(horizontal='center', vertical='center', wrap_text=True)


def _try_merge(ws, min_r: int, min_c: int, max_r: int, max_c: int) -> None:
    """Merge range; ignore if the sheet already has an equivalent merge (template)."""
    try:
        ws.merge_cells(
            start_row=min_r,
            start_column=min_c,
            end_row=max_r,
            end_column=max_c,
        )
    except ValueError:
        pass


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
        template_right_col = ws.max_column
        max_slots = max(
            0, (template_right_col - _FIXED_LEFT_COLS) // _COLS_PER_TEACHER
        )
        extra = len(employees) - max_slots
        if extra > 0:
            ws.insert_cols(template_right_col + 1, extra * _COLS_PER_TEACHER)

        for index, employee in enumerate(employees):
            left = self._teacher_left_col(index, max_slots, template_right_col)
            right = left + 1
            is_new = index >= max_slots
            if is_new:
                _try_merge(ws, 1, left, 1, right)
            hdr = ws.cell(row=1, column=left)
            hdr.value = employee.name

            for weekday in range(6):
                for number in range(8):
                    numerator_row = self._get_numerator_row(weekday, number)
                    denominator_row = numerator_row + 1
                    numerator_lesson = lessons[(employee, weekday, number, False)]
                    denominator_lesson = lessons[(employee, weekday, number, True)]
                    if self._check_merge(numerator_lesson, denominator_lesson):
                        _try_merge(ws, numerator_row, left, denominator_row, right)
                        cl = ws.cell(row=numerator_row, column=left)
                        cl.value = self._get_cell(numerator_lesson)
                        cl.alignment = _CELL_ALIGNMENT
                    else:
                        _try_merge(ws, numerator_row, left, numerator_row, right)
                        cn = ws.cell(row=numerator_row, column=left)
                        cn.value = self._get_cell(numerator_lesson)
                        cn.alignment = _CELL_ALIGNMENT
                        _try_merge(ws, denominator_row, left, denominator_row, right)
                        cd = ws.cell(row=denominator_row, column=left)
                        cd.value = self._get_cell(denominator_lesson)
                        cd.alignment = _CELL_ALIGNMENT

        self._apply_center_alignment_all_schedule_cells(
            ws, employees, max_slots, template_right_col
        )

        if extra > 0:
            max_r = self._get_numerator_row(5, 7) + 1
            anchor_left = template_right_col - 1
            anchor_right = template_right_col
            for pair_i in range(extra):
                new_left = template_right_col + 1 + pair_i * _COLS_PER_TEACHER
                new_right = new_left + 1
                for row in range(1, max_r + 1):
                    src_l = ws.cell(row=row, column=anchor_left)
                    src_r = ws.cell(row=row, column=anchor_right)
                    dst_l = ws.cell(row=row, column=new_left)
                    dst_r = ws.cell(row=row, column=new_right)
                    dst_l.border = copy(src_l.border)
                    dst_r.border = copy(src_r.border)

        wb.save(self.target_filename)
        return self.target_filename

    def _apply_center_alignment_all_schedule_cells(
            self,
            ws,
            employees: list,
            max_slots: int,
            template_right_col: int,
    ) -> None:
        """Центр по горизонтали и вертикали для всей области расписания (включая колонки A–B)."""
        max_r = self._get_numerator_row(5, 7) + 1
        for row in range(1, max_r + 1):
            for col in range(1, ws.max_column + 1):
                ws.cell(row=row, column=col).alignment = _CELL_ALIGNMENT
        for index in range(len(employees)):
            left = self._teacher_left_col(index, max_slots, template_right_col)
            ws.cell(row=1, column=left).font = _HEADER_FONT

    @staticmethod
    def _teacher_left_col(index: int, max_slots: int, template_right_col: int) -> int:
        """1-based Excel column index of the left cell of a teacher pair."""
        if index < max_slots:
            return _FIXED_LEFT_COLS + 1 + index * _COLS_PER_TEACHER
        return (
                template_right_col
                + 1
                + (index - max_slots) * _COLS_PER_TEACHER
        )

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
