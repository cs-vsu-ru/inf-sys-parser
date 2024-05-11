from app.base.utils.schema import extend_schema
from rest_framework import serializers
from rest_framework.response import Response

from app.base.serializers.base import BaseSerializer
from app.base.views.base import BaseView

__all__ = ['EchoView']


# noinspection PyMethodMayBeStatic
class EchoView(BaseView):
    @extend_schema(
        responses={
            200: type(
                'Echo',
                (BaseSerializer,),
                {
                    'GET': serializers.DictField(
                        default={'key': 'value'}, read_only=True
                    ),
                    'POST': serializers.DictField(
                        default={'key': 'value'}, read_only=True
                    ),
                    'data': serializers.CharField(default='Any', read_only=True),
                    'query_params': serializers.DictField(
                        default={'key': 'value'}, read_only=True
                    ),
                    'user': serializers.CharField(read_only=True),
                    'auth': serializers.CharField(read_only=True, required=False),
                    'args': serializers.ListSerializer(
                        child=serializers.CharField(default='Any'), read_only=True
                    ),
                    'kwargs': serializers.DictField(
                        default={'key': 'value'}, read_only=True
                    ),
                    'queries': serializers.IntegerField(read_only=True),
                    'uri': serializers.CharField(read_only=True),
                },
            )
        }
    )
    def get(self, request, *args, **kwargs):
        return Response(
            {
                '__dict__': str(request.__dict__),
            }
        )

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)
