import pandas as pd
from wildfiresapi.models import Wildfires
from django.conf import settings
from django.utils import timezone


def create_wildfire_object(row):

    #aware_datetime = timezone.make_aware(
    #        row['acq_datetime_gmt_3'],
    #        timezone=timezone.get_current_timezone())

    return Wildfires(
        latitude=row['latitude'],
        longitude=row['longitude'],
        brightness=row['brightness'],
        scan=row['scan'],
        track=row['track'],
        acq_date=row['acq_date'].date(),
        acq_time=row['acq_time'],
        satellite=row['satellite'],
        instrument=row['instrument'],
        confidence=row['confidence'],
        version=row['version'],
        bright_t31=row['bright_t31'],
        frp=row['frp'],
        daynight=row['daynight'],
        ftype=row['type'],
        comuna=row['comuna'],
        #acq_datetime_gmt_3=row['acq_datetime_gmt_3'],
    )


# Delete all wildfires
Wildfires.objects.all().delete()

if Wildfires.objects.all().exists():
    print("Data already populated.")
else:
    try:
        # Fill with data from parquet file
        parquet_file_path = 'fires_merged_comunas_timezone.parquet'
        df = pd.read_parquet(parquet_file_path)

        df['acq_date'] = pd.to_datetime(df['acq_date'])
        #df['acq_datetime_gmt_3'] = pd.to_datetime(df['acq_datetime_gmt_3'])
        df['type'] = df['type'].fillna(-1)

        batch_size = 100  # For low memory usag

        for i in range(0, len(df), batch_size):
            batch_df = df.iloc[i:i + batch_size]
            wildfires_list = [
                create_wildfire_object(row) for _, row in batch_df.iterrows()
                ]
            Wildfires.objects.bulk_create(wildfires_list)

        print("Data populated successfully.")
    except Exception as e:
        print("Error:", e)
