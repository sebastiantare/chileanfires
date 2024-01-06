# your_app_name/cron.py

from django.core.management.base import BaseCommand
from .models import Wildfires
import pandas as pd
import os
import logging
logger = logging.getLogger(__name__)

def insert_data():
    csv_path = '../dump/dump.csv'
    success = False

    # Read if there is a file dalled dump.csv and insert data into the database of Wildfires
    with open(csv_path, 'r') as f:
        try:
            df = pd.read_csv(f)
            print(df.head())
            #df.columns = []

            df = df[~(
                (df['latitude'].isin(list(Wildfires.objects.values_list('latitude', flat=True)))) &
                (df['longitude'].isin(list(Wildfires.objects.values_list('longitude', flat=True)))) &
                (df['acq_date'].isin(list(Wildfires.objects.values_list('acq_date', flat=True))))
            )]

            Wildfires.objects.bulk_create(
                Wildfires(**vals) for vals in df.to_dict('records')
            )

            success = True
        except Exception as e:
            print(f"Error inserting data: {e}")
            success = False

    if success:
        try:
            os.remove(csv_path)
            print(f"File '{csv_path}' deleted successfully.")
        except OSError as e:
            print(f"Error deleting file '{csv_path}': {e}")
    print("Data inserted successfully.")
    
