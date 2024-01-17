import pandas as pd
from wildfiresapi.models import Wildfires


def create_wildfire_object(row):
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
        comuna=row['comuna']
    )


# parquet_file_path = 'fires_merged.parquet'
parquet_file_path = 'fires_merged_comunas.parquet'
df = pd.read_parquet(parquet_file_path)

df['acq_date'] = pd.to_datetime(df['acq_date'])

# Make type null values -1
df['type'] = df['type'].fillna(-1)

# Delete previous wildfires
Wildfires.objects.all().delete()

# Check if there is any data in the database, if there is, it exits the script
if Wildfires.objects.all().exists():
    print("Data already populated.")
    exit()

# Set batch size based on available memory
batch_size = 100  # Adjust this value based on your system's memory constraints

# Populate database in batches
for i in range(0, len(df), batch_size):
    batch_df = df.iloc[i:i + batch_size]
    wildfires_list = [
            create_wildfire_object(row) for _, row in batch_df.iterrows()
            ]
    Wildfires.objects.bulk_create(wildfires_list)

print("Data populated successfully.")
