"""
    By Sebastian Tare.
    Main class to store the data captured by NASA FIRMS API,
    and merged by cron jobs.

    Data info() example from Pandas:

     #   Column      Non-Null Count   Dtype
    ---  ------      --------------   -----
     0   latitude    580029 non-null  float64
     1   longitude   580029 non-null  float64
     2   brightness  580029 non-null  float64
     3   scan        580029 non-null  float64
     4   track       580029 non-null  float64
     5   acq_date    580029 non-null  datetime64[ns]
     6   acq_time    580029 non-null  int64
     7   satellite   580029 non-null  object
     8   instrument  580029 non-null  object
     9   confidence  580029 non-null  object
     10  version     580029 non-null  object
     11  bright_t31  580029 non-null  float64
     12  frp         580029 non-null  float64
     13  daynight    580029 non-null  object
     14  type        367685 non-null  float64

"""
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
    #type is reserved
    ftype = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Wildfire at \
            ({self.latitude}, {self.longitude}) on {self.acq_date}"

    def get_datetime(self):
        acq_date_time_str = f"\
        {self.acq_date.strftime('%Y-%m-%d')} \
        {self.acq_time:04d}"

        acq_datetime = datetime.strptime(acq_date_time_str, '%Y-%m-%d %H%M')

        return acq_datetime
