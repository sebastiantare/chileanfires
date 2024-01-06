# your_app_name/cron.py

from django.core.management.base import BaseCommand
from .models import Wildfires
import pandas as pd
import os
from datetime import datetime, timedelta
import logging
import sys
import os
import requests
from time import sleep
import configparser


def get_data(*job_args, **job_kwargs):
    ### Setup
    BASE_DIR = str(job_args[0])
    api_key = str(job_args[1])

    config_path = os.path.join(BASE_DIR, 'config.ini')

    def load_config():
        config = configparser.ConfigParser()
        config.read(config_path)
        return config

    config = load_config()

    output_directory = os.path.join(BASE_DIR, 'dump')

    log_file = os.path.join(BASE_DIR, 'dump/get_data.log')
    logging.basicConfig(filename=log_file,
                        encoding='utf-8', level=logging.INFO)

    ### Functions

    def transformData(df, cols):
        try:
            new_data = df.copy()
            # Preprocess some columns
            new_data['acq_date'] = pd.to_datetime(
                new_data['acq_date']).astype('datetime64[us]')
            # new_data['hour'] = new_data['acq_time'].apply(parse_time)
            # new_data['hour'] = new_data['hour'].dt.components.hours

            logging.info(f"Transform Hour: Done. Shape {new_data.shape}")

            new_data.columns = cols

            # Remove low confidence data
            # new_data = new_data[~(new_data['confidence'] == 'l')]
            # logging.info(f"Filter low confidence: Done. Shape {new_data.shape}")

            return new_data
        except Exception as e:
            logging.error(f"Error preprocessing new data {str(e)}")

    ### Get Data

    try:
        base_url = config.get('API', 'base_url')

        # date - 1 day so it gets all the data in case it's processing today's data.
        current_date = (datetime.now() - timedelta(days=1)
                        ).strftime('%Y-%m-%d')

        # Get max() date from wildfires
        if Wildfires.objects.count() > 0:
            max_date = Wildfires.objects.latest('acq_date').acq_date
            current_date = max_date.strftime('%Y-%m-%d')

        logging.info(
            f"Requesting data with the following parameters Date={current_date}")

        api_url_snpp = config.get('API', 'api_template_snpp').format(
            api_key=api_key, date=current_date)
        api_url_modis = config.get('API', 'api_template_modis').format(
            api_key=api_key, date=current_date)
        api_url_noaa20 = config.get('API', 'api_template_noaa20').format(
            api_key=api_key, date=current_date)

        urls = [api_url_snpp, api_url_modis, api_url_noaa20]

        for i, url in enumerate(urls):
            request_url = base_url + url

            # Get & save data
            response = requests.get(request_url)

            if response.status_code == 200:
                csv_data = response.text

                if csv_data == 'Invalid MAP_KEY.':
                    return logging.info(f"{csv_data} -> Probably too many requests. {datetime.now()}")

                csv_filename = os.path.join(output_directory, f"dump_{i}.csv")

                with open(csv_filename, 'w', newline='') as csv_file:
                    csv_file.write(csv_data)
                logging.info(f"CSV data saved to {csv_filename}")
            else:
                logging.error(
                    f"API request failed with status code {response.status_code}")
            sleep(2)

    except configparser.Error as e:
        logging.error(f"Error reading configuration: {str(e)}")
    except requests.RequestException as e:
        logging.error(f"API request failed: {str(e)}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")

    ### Merge Data

    try:
        config = load_config()

        # How data comes from the API
        # dump_0 country_id,latitude,longitude,bright_ti4,scan,track,acq_date,acq_time,satellite,instrument,confidence,version,bright_ti5,frp,daynight
        # dump_1 country_id,latitude,longitude,brightness,scan,track,acq_date,acq_time,satellite,instrument,confidence,version,bright_t31,frp,daynight
        # dump_2 country_id,latitude,longitude,bright_ti4,scan,track,acq_date,acq_time,satellite,instrument,confidence,version,bright_ti5,frp,daynight

        default_cols = ['latitude', 'longitude', 'brightness', 'scan', 'track', 'acq_date', 'acq_time',
                        'satellite', 'instrument', 'confidence', 'version', 'bright_t31', 'frp', 'daynight']
        db = pd.DataFrame(columns=default_cols)

        # Load files
        output_directory = os.path.join(BASE_DIR, 'dump')

        merged_data = pd.DataFrame(columns=default_cols, dtype='object')

        for i in range(3):
            csv_filename = os.path.join(output_directory, f"dump_{i}.csv")
            new_data = pd.read_csv(csv_filename)
            logging.info(f"New Data Size {new_data.shape}")

            # Drop country CL
            if 'country_id' in new_data.columns:
                new_data.drop('country_id', axis=1, inplace=True)

            if len(new_data.columns) != len(default_cols):
                logging.error(
                    f"Columns do not match. Expected {len(default_cols)}, got {len(new_data.columns)}")
                continue

            new_data_transformed = transformData(new_data, db.columns)

            merged_data = pd.concat(
                [merged_data, new_data_transformed], axis=0)

            logging.info(f"Concatenate: Done. Shape {merged_data.shape}")

            os.remove(csv_filename)
            logging.info(f"Successfully removed file: {csv_filename}")

        # Drop duplicates
        # merged_data.drop_duplicates(inplace=True)
        # merged_data.reset_index(drop=True, inplace=True)
        # logging.info(f"Drop Duplicates: Done. Shape {merged_data.shape}")

        # Save to csv
        csv_filename = os.path.join(output_directory, f"dump.csv")
        merged_data.to_csv(csv_filename, index=False)
        logging.info(f"Saving to csv: {csv_filename}")

    except FileNotFoundError:
        logging.error(f"The file {csv_filename} does not exist.")
    except PermissionError:
        logging.error(
            f"You don't have permission to delete the file {csv_filename}.")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")

    ### Insert data in PostrgreSQL

    # Get new data path
    csv_path = os.path.join(BASE_DIR, 'dump/dump.csv')
    success = False

    # Read if there is a file dalled dump.csv and insert data into the database of Wildfires
    with open(csv_path, 'r') as f:
        try:
            df = pd.read_csv(f)

            logging.info(f"Rows to insert {df.shape[0]}")

            # Filter out duplicates
            df = df[~(
                (df['latitude'].isin(list(Wildfires.objects.values_list('latitude', flat=True)))) &
                (df['longitude'].isin(list(Wildfires.objects.values_list('longitude', flat=True)))) &
                (df['acq_date'].isin(
                    list(Wildfires.objects.values_list('acq_date', flat=True))))
            )]

            logging.info(f"Filtered rows to insert {df.shape[0]}")

            if df.shape[0] == 0:
                logging.info("No new data to insert.")
                return

            wildfires_list = []

            for index, row in df.iterrows():
                wildfire = Wildfires(
                    latitude=row['latitude'],
                    longitude=row['longitude'],
                    brightness=row['brightness'],
                    scan=row['scan'],
                    track=row['track'],
                    acq_date=row['acq_date'],
                    acq_time=row['acq_time'],
                    satellite=row['satellite'],
                    instrument=row['instrument'],
                    confidence=row['confidence'],
                    version=row['version'],
                    bright_t31=row['bright_t31'],
                    frp=row['frp'],
                    daynight=row['daynight']
                    #type doesn't come in the api requests
                )
                wildfires_list.append(wildfire)

            Wildfires.objects.bulk_create(wildfires_list)
            success = True
        except Exception as e:
            logging.error(f"Error inserting data: {e}")
            success = False

    if success:
        try:
            os.remove(csv_path)
            logging.info(f"File '{csv_path}' deleted successfully.")
        except OSError as e:
            logging.error(f"Error deleting file '{csv_path}': {e}")
    logging.info("Data inserted successfully.")
