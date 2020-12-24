from asgiref.sync import sync_to_async
from rest_framework import serializers


class ParentSerializer(serializers.Serializer):
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    @sync_to_async
    def is_valid(self, *args, **kwargs):
        return super().is_valid(*args, **kwargs)
