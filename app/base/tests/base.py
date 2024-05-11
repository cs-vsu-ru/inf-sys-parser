from typing import Type

from django.db import models
from django.forms import model_to_dict
from rest_framework.test import APITestCase


class BaseTest(APITestCase):
    assert_equal = APITestCase.assertEqual
    assert_contains = APITestCase.assertContains
    assert_in = APITestCase.assertIn
    assert_true = APITestCase.assertTrue
    assert_false = APITestCase.assertFalse
    assert_dict_equal = APITestCase.assertDictEqual
    assert_is_instance = APITestCase.assertIsInstance
    assert_is_none = APITestCase.assertIsNone
    assert_is_not_none = APITestCase.assertIsNotNone

    def assert_json(self, json: dict, exp_json: dict):
        def dfs(inner_json, inner_exp_json):
            def visit(exp_key, exp_value):
                self.assert_in(exp_key, inner_json)
                value = inner_json[exp_key]
                if callable(exp_value):
                    if exp_value(value) is False:
                        self.fail(f'{exp_key = }, {value = }')
                else:
                    self.assert_is_instance(value, type(exp_value))
                    if isinstance(value, dict):
                        dfs(value, exp_value)
                    else:
                        self.assert_equal(value, exp_value)

            [visit(*items) for items in inner_exp_json.items()]

        dfs(json, exp_json)

    def assert_instance(self, instance: models.Model, instance_data: dict):
        self.assert_json(model_to_dict(instance), instance_data)

    def assert_model(
        self,
        model: Type[models.Model] | models.Manager | models.QuerySet | models.Model,
        instance_data: dict,
        **filters,
    ):
        match model:
            case type():
                return self.assert_model(model.objects, instance_data, **filters)
            case models.Manager():
                return self.assert_model(model.all(), instance_data, **filters)
            case models.QuerySet():
                try:
                    return self.assert_model(
                        model.filter(**filters or {}).get(), instance_data
                    )
                except model.model.DoesNotExist:
                    self.fail(
                        f'{model.model.__name__} matching query ({filters}) does not '
                        f'exists'
                    )
            case _:
                self.assert_instance(model, instance_data)
        return model
