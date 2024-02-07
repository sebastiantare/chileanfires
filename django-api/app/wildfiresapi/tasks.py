from __future__ import absolute_import, unicode_literals
from celery import shared_task
from .models import Wildfires
import pandas as pd
import geopandas as gpd
import os
from datetime import datetime
import logging
import requests
from time import sleep
from django.conf import settings
from shapely.geometry import Point
# import celery app
from api.celery import app
import xgboost as xgb
import numpy as np


@app.task
def get_data():
    BASE_DIR = settings.BASE_DIR
    api_key = settings.NASA_FIRMS_TOKEN

    output_directory = os.path.join(BASE_DIR, 'dump')

    log_file = os.path.join(output_directory, 'get_data.log')
    logging.basicConfig(filename=log_file,
                        encoding='utf-8', level=logging.INFO)

    # Check if there is any data in the database Wildfires
    if Wildfires.objects.count() == 0:
        logging.info("No data found, waiting for populate the database.")
        return

    # Get Data
    try:
        # NASA API
        base_url = "https://firms.modaps.eosdis.nasa.gov"

        # - timedelta(days=1)
        current_date = datetime.now().strftime('%Y-%m-%d')

        max_date = Wildfires.objects.latest('acq_date').acq_date
        current_date = max_date.strftime('%Y-%m-%d')

        logging.info(
            "Requesting data with the following"
            f"parameters Date={current_date}")

        api_url_snpp = f"/api/country/csv/{api_key}" \
                       f"/VIIRS_SNPP_NRT/CHL/10/{current_date}"
        api_url_modis = f"/api/country/csv/{api_key}" \
                        f"/MODIS_NRT/CHL/10/{current_date}"
        api_url_noaa20 = f"/api/country/csv/{api_key}" \
                         f"/VIIRS_NOAA20_NRT/CHL/10/{current_date}"

        urls = [api_url_snpp, api_url_modis, api_url_noaa20]

        for i, url in enumerate(urls):
            request_url = base_url + url

            response = requests.get(request_url)

            if response.status_code == 200:
                csv_data = response.text

                if csv_data == 'Invalid MAP_KEY.':
                    return logging.info(
                            f"{csv_data} ->"
                            f" Probably too many requests."
                            f"{datetime.now()}")

                csv_filename = os.path.join(output_directory, f"dump_{i}.csv")

                with open(csv_filename, 'w', newline='') as csv_file:
                    csv_file.write(csv_data)
                logging.info(f"CSV data saved to {csv_filename}")
            else:
                logging.error(
                    f"API request failed with"
                    f"status code {response.status_code}")
            sleep(2)

        # Invoke shared_task to merge data
        merge_data.delay()

    except requests.RequestException as e:
        logging.error(f"API request failed: {str(e)}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")


@shared_task
def merge_data():
    BASE_DIR = settings.BASE_DIR

    def transform_data(df, cols):
        try:
            df = df.copy()
            # Preprocess some columns
            df['acq_date'] = pd.to_datetime(
                df['acq_date']).astype('datetime64[us]')
            # df['hour'] = df['acq_time'].apply(parse_time)
            # df['hour'] = df['hour'].dt.components.hours

            logging.info(f"Transform Hour: Done. Shape {df.shape}")

            df.columns = cols

            return df
        except Exception as e:
            logging.error(f"Error preprocessing new data {str(e)}")

    try:
        default_cols = ['latitude', 'longitude', 'brightness', 'scan',
                        'track', 'acq_date', 'acq_time',
                        'satellite', 'instrument', 'confidence', 'version',
                        'bright_t31', 'frp', 'daynight']
        db = pd.DataFrame(columns=default_cols)

        # Load files
        output_directory = os.path.join(BASE_DIR, 'dump')

        merged_data = pd.DataFrame(columns=default_cols, dtype='object')

        try:
            for i in range(3):
                csv_filename = os.path.join(output_directory, f"dump_{i}.csv")
                df = pd.read_csv(csv_filename)
                logging.info(f"New data of size {df.shape}")

                # Drop country CL
                if 'country_id' in df.columns:
                    df.drop('country_id', axis=1, inplace=True)

                if len(df.columns) != len(default_cols):
                    logging.error(
                        f"Columns do not match. Expected {len(default_cols)},"
                        f"got {len(df.columns)}")
                    continue

                df_transformed = transform_data(
                        df,
                        db.columns
                        )

                merged_data = pd.concat(
                    [merged_data, df_transformed], axis=0)

                logging.info(f"Concatenate: Done. Shape {merged_data.shape}")

                os.remove(csv_filename)
                logging.info(f"Successfully removed file: {csv_filename}")
        except Exception as e:
            logging.error(f"Error merging data: {str(e)}")

        # Filter points that fall within the areas to ignore
        def filter_by_area(
                    points_df, polygons_df,
                    lat_col='latitude',
                    lon_col='longitude'
                     ):
            points_gdf = gpd.GeoDataFrame(
                    points_df,
                    geometry=gpd.points_from_xy(
                        points_df[lat_col],
                        points_df[lon_col])
                    )
            filtered_points = points_gdf[
                    ~(points_gdf.within(polygons_df.unary_union))]
            return points_df[points_df.index.isin(filtered_points.index)]

        # Drop duplicates
        # merged_data.drop_duplicates(inplace=True)
        # merged_data.reset_index(drop=True, inplace=True)
        # logging.info(f"Drop Duplicates: Done. Shape {merged_data.shape}")

        # Filter Volcanoes and Static data like solar panels from data

        # Read areas for point filtering
        geojson_path = os.path.join(BASE_DIR, 'data/ignore_areas.geojson')

        try:
            before_size = merged_data.shape[0]
            gdf_areas = gpd.read_file(geojson_path, driver='GeoJSON')

            merged_data = filter_by_area(merged_data, gdf_areas)

            after_size = merged_data.shape[0]
            logging.info(f"Filtered points from {before_size} to {after_size}")
        except Exception as e:
            return logging.error(
                    "Error in filtering points by area: "
                    f"{str(e)}")

        # Page 51
        # https://modis-fire.umd.edu/files/MODIS_C6_C6.1_Fire_User_Guide_1.0.pdf
        def convert_confidence(confidence):
            # Check if confidence is not a number
            if confidence == 'l':
                return 'l'
            elif confidence == 'n':
                return 'n'
            elif confidence == 'h':
                return 'h'
            confidence_val = int(confidence)

            if confidence_val >= 80:
                return 'h'
            elif 30 <= confidence_val < 80:
                return 'n'
            else:
                return 'l'

        merged_data['confidence'] = merged_data['confidence'].apply(
                convert_confidence)
        merged_data['confidence'] = merged_data['confidence'].astype(
                str)

        # Map the datapoints to comunas
        def tag_comuna(row, comunas_df):
            point = Point(row['longitude'], row['latitude'])
            for i, row in comunas_df.iterrows():
                if point.within(row['geometry']):
                    # TODO: comunas overlap so I return the first one,
                    #       so in the future would be interesting to
                    #       have this set to an array of comunas.
                    return row['comuna']
            return None

        comunas_path = os.path.join(BASE_DIR, 'data/comunas.geojson')

        gdf_comunas = gpd.read_file(comunas_path, driver='GeoJSON')

        merged_data['comuna'] = merged_data.apply(
                tag_comuna, axis=1, args=(gdf_comunas,))

        # Parse datetime to match Chilean timezone
        def parse_time(value):
            hours = value // 100
            minutes = value % 100
            return pd.Timedelta(hours=hours, minutes=minutes)

        # Save to csv
        csv_filename = os.path.join(output_directory, "dump.csv")
        merged_data.to_csv(csv_filename, index=False)
        logging.info(f"Saving to csv: {csv_filename}")

        # Insert data into the database
        classify_data.delay()

    except FileNotFoundError:
        logging.error(f"The file {csv_filename} does not exist.")
    except PermissionError:
        logging.error(
            f"You don't have permission to delete the file {csv_filename}.")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")


@shared_task
def classify_data():
    BASE_DIR = settings.BASE_DIR

    csv_path = os.path.join(BASE_DIR, 'dump/dump.csv')

    with open(csv_path, 'r') as f:
        try:
            df = pd.read_csv(f)
            logging.info(f"Rows to process {df.shape[0]}")

            df['acq_date'] = pd.to_datetime(
                    df['acq_date']).astype('datetime64[us]')

            # Filter out existing points before processing
            for index, row in df.iterrows():
                if Wildfires.objects.filter(
                        latitude=row['latitude'],
                        longitude=row['longitude'],
                        acq_date=row['acq_date'],
                        acq_time=row['acq_time'],
                        frp=row['frp'],
                        track=row['track']
                        ).exists():
                    # Remove row from df
                    df.drop(index, inplace=True)
                    continue

            if df.shape[0] == 0:
                logging.info("No new data to process...")
                return

            # Load xgboost model
            model_path = os.path.join(BASE_DIR, 'data/xgb_model.json')
            model = xgb.XGBClassifier()
            model.load_model(model_path)

            # Prepare for prediction
            features = [
                    'frp', 'track', 'daynight', 'confidence',
                    'latitude', 'longitude'
                    ]

            df_predictions = df[features].copy()

            # Categorical cols to numeric
            if 'daynight' in df_predictions.columns:
                df_predictions['daynight'] = \
                        df_predictions['daynight'].apply(
                            lambda x: 1 if x != 'D' else 0)
                df_predictions['daynight'] = \
                    df_predictions['daynight'].astype(int)

            if 'confidence' in df_predictions.columns:
                df_predictions['confidence'] = \
                    df_predictions['confidence'].apply(
                        lambda x: 0 if x == 'l' else 1
                        if x == 'n' else 2 if x == 'h' else 3)
                df_predictions['confidence'] = \
                    df_predictions['confidence'].astype(int)

            preds = model.predict(df_predictions)
            preds = np.where(preds > 0.5, 1, 0)

            df['ftype'] = preds

            # Filter non-wildfire data
            logging.info(f"Non-wildfires rows: {preds[preds == 1].shape[0]}")

            # Wildfire data
            logging.info(f"Wildfires rows: {preds[preds == 0].shape[0]}")

            # Save to replace old dump.csv
            df.to_csv(csv_path, index=False)
            logging.info(f"Saving to csv: {csv_path}")

            # Next task
            insert_data.delay()

        except Exception as e:
            logging.error(f"Error inserting data: {e}")


@shared_task
def insert_data():
    # Insert data in PostgreSQL
    BASE_DIR = settings.BASE_DIR

    # Get new data path
    csv_path = os.path.join(BASE_DIR, 'dump/dump.csv')
    success = False

    # Read if there is a file dalled dump.csv
    # and insert data into the database of Wildfires
    with open(csv_path, 'r') as f:
        try:
            df = pd.read_csv(f)
            df['acq_date'] = pd.to_datetime(
                    df['acq_date']).astype('datetime64[us]')
            logging.info(f"Rows to insert: {df.shape[0]}")

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
                    daynight=row['daynight'],
                    ftype=row['ftype'],
                    comuna=row['comuna'],
                )
                wildfires_list.append(wildfire)

            logging.info(f"Rows to insert after filtering: "
                         f"{len(wildfires_list)}")
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
