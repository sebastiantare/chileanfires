#wildfiresapi/viewsets.py
from rest_framework import permissions, viewsets
from django.db.models import Max, Count
from . import models
from . import serializers
from rest_framework.decorators import action
from datetime import datetime, timedelta, timezone

class WildfiresViewset(viewsets.ReadOnlyModelViewSet):
    """
        Returns the latest wildfires.
    """
    max_acq_date = models.Wildfires.objects.all().aggregate(Max('acq_date'))['acq_date__max']
    queryset = models.Wildfires.objects.filter(acq_date=max_acq_date)
    serializer_class = serializers.WildfiresSerializer

class WildfiresViewset12Months(viewsets.ReadOnlyModelViewSet):
    """
        Returns count of all fires occurring by month in the last 12 months.
    """
    serializer_class = serializers.MonthlyWildfiresSerializer

    def get_queryset(self):
        # Calculate the date 12 months ago from today
        twelve_months_ago = datetime.now() - timedelta(days=365)

        # Query to get the count of fires occurring by month in the last 12 months
        queryset = models.Wildfires.objects.filter(acq_date__gte=twelve_months_ago) \
                                           .extra({'month': "EXTRACT(month FROM acq_date)"}) \
                                           .values('month') \
                                           .annotate(fire_count=Count('id')) \
                                           .order_by('month')

        return queryset
