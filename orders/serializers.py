from rest_framework import serializers
from .models import Order, Part, PART_STATUS


class PartSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    storage = serializers.SerializerMethodField()

    class Meta:
        model = Part
        fields = ['number', 'storage', 'status']

    def get_status(self, obj: Part):
        return dict(PART_STATUS)[obj.status]

    def get_storage(self, obj: Part):
        return str(obj.storage)


class OrderSerializer(serializers.ModelSerializer):
    part = PartSerializer()

    class Meta:
        model = Order
        fields = ['id', 'number', 'name', 'clientid', 'part', 'date']