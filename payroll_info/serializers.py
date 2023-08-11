from rest_framework import serializers
from .models import *


class InterbankUSDRateSerializer(serializers.ModelSerializer):
    # format date to be in the format "%m-%d-%Y"
    date = serializers.DateField(format="%m-%d-%Y")

    class Meta:
        model = InterbankUSDRate
        fields = ['rate', 'date']


class NECSerializer(serializers.ModelSerializer):
    class Meta:
        model = NEC
        fields = ['id', 'name']


class NECRatesSerializer(serializers.ModelSerializer):
    # format date to be in the format "%m-%d-%Y"
    date = serializers.DateField(format="%m-%d-%Y")

    class Meta:
        model = Rates
        fields = ['nec', 'rate', 'date']


class GradesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grades
        fields = ['nec', 'grade', 'usd_minimum']
