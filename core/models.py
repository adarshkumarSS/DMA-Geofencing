from django.db import models
from django.db import models


# Create your models here.
class EVChargingLocation(models.Model):
    station_name = models.CharField(max_length=250)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.station_name

class District(models.Model):
    dtname = models.CharField(max_length=100)
    stname = models.CharField(max_length=100)
    stcode11 = models.CharField(max_length=10)
    dtcode11 = models.CharField(max_length=10)
    year_stat = models.CharField(max_length=20)
    objectid = models.IntegerField()
    dist_lgd = models.IntegerField()
    state_lgd = models.IntegerField()
    coordinates = models.JSONField()  # Use django.db.models.JSONField

    def __str__(self):
        return self.dtname
