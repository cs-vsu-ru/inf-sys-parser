from typing import Any, Callable
from urllib.parse import urlencode

from app.base.exceptions import APIWarning
from app.base.tests.base import BaseTest
from app.users.models import Token, User
from app.users.tests.factories.token import TokenFactory
from app.users.tests.factories.users import UserFactory


class _MeType(User):
    raw_password: str
    auth_token: Token

    class Meta:
        abstract = True


class BaseViewTest(BaseTest):
    path: str

    me_class: Callable[..., User] = UserFactory
    me_data: dict[str, Any] | None = {}
    _me = None

    @property
    def me(self) -> _MeType | None:
        if self._me is None:
            if self.me_data is None:
                return None
            self.me = self.me_class(**self.me_data)
        return self._me

    @me.setter
    def me(self, me_):
        del self.me
        self._me = me_
        self.client.force_login(self.me)
        self.me.auth_token = TokenFactory(user=self.me)

    @me.deleter
    def me(self):
        if self._me is not None:
            self.client.logout()
            self._me.auth_token.delete()
            self._me.delete()
            self._me = None

    def setUp(self):
        _ = self.me

    def get(self, path=None, query=None):
        return self.client.get(f'{path or self.path}?{urlencode(query or {})}')

    def post(self, path=None, data=None):
        return self.client.post(path or self.path, data)

    def put(self, path=None, data=None):
        return self.client.put(path or self.path, data)

    def patch(self, path=None, data=None):
        return self.client.patch(path or self.path, data)

    def delete(self, path=None, data=None):
        return self.client.delete(path or self.path, data)

    def assert_response(self, response, status=200, data: dict = None):
        self.assert_equal(response.status_code, status)
        self.assert_json(response.json() if response.content else {}, data or {})

    def _test(
        self,
        method: str,
        exp_data: dict[str, Any] | APIWarning = None,
        data: dict[str, Any] = None,
        status: int = None,
        path: str = None,
    ):
        response = getattr(self, method)(path, data)
        if response.content:
            status = status or {'post': 201, 'delete': 204}.get(method, 200)
        else:
            status = 204
        if isinstance(exp_data, APIWarning):
            status = exp_data.status
            exp_data = exp_data.serialize()
        self.assert_response(response, status, exp_data)
