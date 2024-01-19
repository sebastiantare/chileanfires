from datetime import datetime
from django.db import models

# Create your models here.


class Wildfires(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    brightness = models.FloatField()
    scan = models.FloatField()
    track = models.FloatField()
    acq_date = models.DateField()
    acq_time = models.IntegerField()
    satellite = models.CharField(max_length=255)
    instrument = models.CharField(max_length=255)
    confidence = models.CharField(max_length=255)
    version = models.CharField(max_length=255)
    bright_t31 = models.FloatField()
    frp = models.FloatField()
    daynight = models.CharField(max_length=255)
    ftype = models.FloatField(null=True, blank=True)
    comuna = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Wildfire at \
            ({self.latitude}, {self.longitude}) on {self.acq_date}"

    def get_datetime(self):
        acq_date_time_str = f"\
            {self.acq_date.strftime('%Y-%m-%d')} {self.acq_time:04d}"

        acq_datetime = datetime.strptime(acq_date_time_str, '%Y-%m-%d %H%M')

        return acq_datetime
