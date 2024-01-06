# populate_database.py
import pandas as pd
from datetime import datetime
from wildfiresapi.models import Wildfires

parquet_file_path = 'fires_merged.parquet'
df = pd.read_parquet(parquet_file_path)

df['acq_date'] = pd.to_datetime(df['acq_date'])

# Make type null values -1
df['type'] = df['type'].fillna(-1)

# Delete previous wildfires
Wildfires.objects.all().delete()

# Populate database

wildfires_list = []
for index, row in df.iterrows():
    wildfire = Wildfires(
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
        ftype=row['type']
    )
    wildfires_list.append(wildfire)

Wildfires.objects.bulk_create(wildfires_list)

print("Data populated successfully.")