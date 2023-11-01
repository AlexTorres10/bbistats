from django.db import models

class Result(models.Model):
    idresults = models.AutoField(primary_key=True)
    casa = models.CharField(max_length=100)
    placar = models.CharField(max_length=10)
    fora = models.CharField(max_length=100)
    data = models.DateField()
    liga = models.CharField(max_length=100)

    class Meta:
        db_table = 'results'
        ordering = ['-data']  # Order results by date in descending order

class Time(models.Model):
    idtimes = models.AutoField(primary_key=True)
    time = models.CharField(max_length=100)
    divisao = models.CharField(max_length=100)
    url = models.CharField(max_length=100)

    class Meta:
        db_table = 'times'