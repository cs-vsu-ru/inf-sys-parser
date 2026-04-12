from rest_framework import serializers

from app.base.serializers.base import BaseModelSerializer, BaseSerializer
from app.lessons.models import WeekConfig


class GET_WeekConfigSerializer(BaseModelSerializer):
    current_is_denominator = serializers.SerializerMethodField()

    class Meta:
        model = WeekConfig
        read_only_fields = ['reference_date', 'is_denominator', 'current_is_denominator']

    def get_current_is_denominator(self, obj: WeekConfig) -> bool:
        return obj.get_current_is_denominator()


class PATCH_WeekConfigSerializer(BaseModelSerializer):
    class Meta:
        model = WeekConfig
        write_only_fields = ['reference_date', 'is_denominator']

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def create(self, validated_data):
        return WeekConfig.objects.create(**validated_data)

    def to_representation(self, instance):
        return GET_WeekConfigSerializer(instance).data
