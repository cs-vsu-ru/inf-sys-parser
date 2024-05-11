import datetime
from typing import Callable, Final

from factory import Faker as _FactoryFaker
from faker import Faker as _Faker


class SubFaker(_Faker):
    first_name: Callable[..., str]
    last_name: Callable[..., str]
    password: Callable[..., str]
    email: Callable[..., str]
    future_date: Callable[..., datetime.date]

    def random_string(self, length: int = 10):
        letters_count = self.random_int(max=length)
        letters = self.random_letters(letters_count)
        numbers = [str(self.random_digit()) for _ in range(length - letters_count)]
        return ''.join(self.random_elements(letters + numbers, length, True))


class Faker(_FactoryFaker):
    @classmethod
    def _get_faker(cls, locale=None):
        if locale is None:
            locale = cls._DEFAULT_LOCALE

        if locale not in cls._FAKER_REGISTRY:
            sub_faker = SubFaker(locale=locale).unique
            cls._FAKER_REGISTRY[locale] = sub_faker

        return cls._FAKER_REGISTRY[locale]


fake: Final[SubFaker] = SubFaker()
