from collections import defaultdict

from app.employees.models import Employee
from app.lessons.entites.cell import CellEntity


class CellsFixer:
    def __init__(self):
        self.employee_manager = Employee.objects
    
    def fix(self, cells: list[CellEntity]) -> dict[Employee, list[CellEntity]]:
        fixed_cells: dict[Employee, list[CellEntity]] = defaultdict(list)
        employee_map = self._get_employee_map()
        first_cell_map: dict[Employee, CellEntity] = {}
        for cell in cells:
            if employee := employee_map.get(cell.employee_name):
                try:
                    first_cell = first_cell_map[employee]
                    if first_cell.placement == cell.placement:
                        cell.name = first_cell.name
                        fixed_cells[employee].append(cell)
                except KeyError:
                    first_cell_map[employee] = cell
                    fixed_cells[employee].append(cell)
        return fixed_cells

    def _get_employee_map(self) -> dict[str, Employee]:
        return {employee.name: employee for employee in self.employee_manager.all()}
