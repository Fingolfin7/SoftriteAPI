from django.db import models
from datetime import datetime


class InterbankUSDRate(models.Model):
    # Interbank USD to ZWL middle Rate
    date = models.DateField(default=datetime.today, unique=True)
    rate = models.FloatField()

    def __str__(self):
        return f'{datetime.strftime(self.date, "%d %b %Y")}'

    class Meta:
        verbose_name_plural = "Interbank USD Rates"


class NEC(models.Model):
    # track the different necs e.g. Agri, Mining, e.t.c.
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "NECs"

    def __str__(self):
        return f'{self.name} NEC'


class Rates(models.Model):
    # each nec has a rate
    nec = models.ForeignKey(NEC, on_delete=models.CASCADE)
    rate = models.FloatField()
    date = models.DateField(default=datetime.today)

    class Meta:
        verbose_name_plural = "NEC Rates"

    def __str__(self):
        return f'{self.nec.name} Nec Rate on {self.date}'


class Grades(models.Model):
    # each nec has a set of grades
    nec = models.ForeignKey(NEC, on_delete=models.CASCADE, null=True)
    grade = models.CharField(max_length=2)
    usd_minimum = models.FloatField()

    class Meta:
        verbose_name_plural = "NEC USD Grades"

    def __str__(self):
        return f'{self.nec.name} Grade {self.grade}'


