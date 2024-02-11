# wildfiresapi/viewsets.py
from rest_framework import permissions, viewsets, status
from django.db.models import Max, Count
from . import models
from . import serializers
from rest_framework.decorators import action
from datetime import datetime, timedelta, timezone
from django.db.models.functions import TruncDate, TruncMonth
from django_ratelimit.decorators import ratelimit
from django.db import connection
from django.utils.decorators import method_decorator
from rest_framework.response import Response


@method_decorator(ratelimit(key='user', rate='10/m', block=True),
                  name='dispatch')
class WildfiresViewset(viewsets.ReadOnlyModelViewSet):
    """
        Returns the latest wildfires.
    """
    serializer_class = serializers.WildfiresSerializer

    def get_queryset(self):
        max_acq_date = models.Wildfires.objects.all().aggregate(
            Max('acq_date'))['acq_date__max']
        queryset = models.Wildfires.objects.filter(
                acq_date=max_acq_date,
                ftype=0
                )
        return queryset


@method_decorator(ratelimit(key='user', rate='10/m', block=True),
                  name='dispatch')
class WildfiresByDateViewset(viewsets.ReadOnlyModelViewSet):
    """
        Returns wildfires by GMT Date.
    """
    serializer_class = serializers.WildfiresSerializer

    def get_queryset(self):
        date_param = self.request.query_params.get('date', None)
        date_param = datetime.strptime(date_param, '%Y-%m-%d').date()
        print(date_param)

        if date_param is not None:
            queryset = models.Wildfires.objects.filter(
                acq_date=date_param,
                ftype=0
                )
            return queryset
        return Response(status=status.HTTP_400_BAD_REQUEST)


@method_decorator(ratelimit(key='user', rate='10/m', block=True),
                  name='dispatch')
class WildfiresViewset12Months(viewsets.ReadOnlyModelViewSet):
    """
        Returns count of all fires occurring by month in the last 12 months.
    """
    serializer_class = serializers.MonthlyWildfiresSerializer

    def get_queryset(self):
        last_year = datetime.now().year - 1
        print(last_year)

        raw_sql = """
            SELECT
                EXTRACT(MONTH FROM acq_date) AS month,
                COUNT(id) AS fire_count
            FROM wildfiresapi_wildfires
            WHERE EXTRACT(YEAR FROM acq_date) = %s
            GROUP BY month
            ORDER BY month
        """

        with connection.cursor() as cursor:
            cursor.execute(raw_sql, [last_year])
            rows = cursor.fetchall()

        queryset = [
            {'month': row[0], 'fire_count': row[1]} for row in rows
        ]

        return queryset
