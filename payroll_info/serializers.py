from rest_framework import serializers
from .models import InterbankUSDRate, NEC, Grades


class InterbankUSDRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterbankUSDRate
        fields = ['rate', 'date']


class NECSerializer(serializers.ModelSerializer):
    class Meta:
        model = NEC
        fields = ['id', 'name']


class GradesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grades
        fields = ['grade', 'usd_minimum']
