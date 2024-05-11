from app.base.tests.factories.base import BaseFactory
from app.base.tests.fakers import Faker
from app.employees.models import Employee


class EmployeeFactory(BaseFactory):
    id = Faker('random_int')

    class Meta:
        model = Employee
