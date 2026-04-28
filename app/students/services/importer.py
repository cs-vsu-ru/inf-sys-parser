from dataclasses import dataclass, field
from typing import Any

from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from openpyxl import load_workbook

from app.students.models.student import Student


REQUIRED_COLUMNS = {
    'ФИО': 'full_name',
    'Логин': 'login',
    'Email': 'email',
    'Курс': 'course',
    'Группа': 'group',
    'Подгруппа': 'subgroup',
    'Профиль обучения': 'education_profile',
}

OPTIONAL_COLUMNS = {
    'Вид учебной деятельности': 'activity_type',
}

ACTIVITY_MAP = {
    'студент': Student.ACTIVITY_STUDENT,
    'магистрант': Student.ACTIVITY_MASTER,
    'аспирант': Student.ACTIVITY_PHD,
}


@dataclass
class ImportResult:
    created: int = 0
    updated: int = 0
    errors: list[dict[str, Any]] = field(default_factory=list)


class StudentsXlsxImporter:
    def import_file(self, file) -> ImportResult:
        result = ImportResult()

        workbook = load_workbook(file, read_only=True, data_only=True)
        sheet = workbook.active

        rows = sheet.iter_rows(values_only=True)

        try:
            headers_row = next(rows)
        except StopIteration:
            result.errors.append({
                'row': 1,
                'field': 'file',
                'message': 'Файл пустой',
            })
            return result

        headers = [
            str(value).strip() if value is not None else ''
            for value in headers_row
        ]

        missing_columns = [
            column for column in REQUIRED_COLUMNS.keys()
            if column not in headers
        ]
        if missing_columns:
            result.errors.append({
                'row': 1,
                'field': 'headers',
                'message': (
                    'Отсутствуют обязательные колонки: '
                    + ', '.join(missing_columns)
                ),
            })
            return result

        for row_number, row in enumerate(rows, start=2):
            row_data = dict(zip(headers, row))

            if self._is_empty_row(row_data):
                continue

            try:
                data = self._normalize_row(row_data)
                student, created = Student.objects.update_or_create(
                    login=data['login'],
                    defaults=data,
                )
                if created:
                    result.created += 1
                else:
                    result.updated += 1
            except Exception as exc:
                result.errors.append({
                    'row': row_number,
                    'field': 'row',
                    'message': str(exc),
                })

        return result

    def _is_empty_row(self, row_data: dict[str, Any]) -> bool:
        return all(
            value is None or str(value).strip() == ''
            for value in row_data.values()
        )

    def _normalize_row(self, row_data: dict[str, Any]) -> dict[str, Any]:
        data = {}

        for xlsx_column, model_field in REQUIRED_COLUMNS.items():
            value = row_data.get(xlsx_column)
            if value is None or str(value).strip() == '':
                raise ValueError(f'Поле "{xlsx_column}" обязательно')
            data[model_field] = str(value).strip()

        for xlsx_column, model_field in OPTIONAL_COLUMNS.items():
            value = row_data.get(xlsx_column)
            data[model_field] = (
                str(value).strip() if value is not None and str(value).strip() != ''
                else None
            )

        data['login'] = data['login'].lower()
        data['email'] = data['email'].lower()
        self._validate_email(data['email'])

        try:
            data['course'] = int(float(data['course']))
        except (TypeError, ValueError):
            raise ValueError('Поле "Курс" должно быть числом')

        data['activity_type'] = self._normalize_activity_type(
            data.get('activity_type')
        )

        return data

    def _validate_email(self, email: str) -> None:
        try:
            validate_email(email)
        except ValidationError as exc:
            raise ValueError('Некорректный Email') from exc

    def _normalize_activity_type(self, value: str | None) -> str | None:
        if value is None:
            return None

        normalized = value.strip().lower()
        if normalized not in ACTIVITY_MAP:
            raise ValueError(
                'Поле "Вид учебной деятельности" должно быть одним из: '
                'студент / магистрант / аспирант'
            )
        return ACTIVITY_MAP[normalized]