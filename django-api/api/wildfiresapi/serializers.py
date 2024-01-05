# wildfiresapi/serializers.py
from rest_framework import serializers
from .models import Wildfires


class WildfiresSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wildfires
        fields = '__all__'


class MonthlyWildfiresSerializer(serializers.Serializer):
    month = serializers.IntegerField()
    fire_count = serializers.IntegerField()
