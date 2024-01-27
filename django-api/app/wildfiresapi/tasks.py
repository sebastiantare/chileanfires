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


@shared_task
def get_data():
    BASE_DIR = settings.BASE_DIR
    api_key = settings.MAPBOX_TOKEN

    print("Test Print")

    output_directory = os.path.join(BASE_DIR, 'dump')

    log_file = os.path.join(output_directory, 'get_data.log')
    logging.basicConfig(filename=log_file,
                        encoding='utf-8', level=logging.INFO)

    # Get Data

    try:
        # NASA API
        base_url = "https://firms.modaps.eosdis.nasa.gov"

        # - timedelta(days=1)
        current_date = datetime.now().strftime('%Y-%m-%d')

        if Wildfires.objects.count() > 0:
            max_date = Wildfires.objects.latest('acq_date').acq_date
            current_date = max_date.strftime('%Y-%m-%d')

        logging.info(
            f"Requesting data with the following \
            parameters Date={current_date}")

        api_url_snpp = f"/api/country/csv/{api_key}\
                /VIIRS_SNPP_NRT/CHL/10/{current_date}"
        api_url_modis = f"/api/country/csv/{api_key}\
                /MODIS_NRT/CHL/10/{current_date}"
        api_url_noaa20 = f"/api/country/csv/{api_key}\
                /VIIRS_NOAA20_NRT/CHL/10/{current_date}"

        urls = [api_url_snpp, api_url_modis, api_url_noaa20]

        for i, url in enumerate(urls):
            request_url = base_url + url

            response = requests.get(request_url)

            if response.status_code == 200:
                csv_data = response.text

                if csv_data == 'Invalid MAP_KEY.':
                    return logging.info(f"{csv_data} -> \
                    Probably too many requests. {datetime.now()}")

                csv_filename = os.path.join(output_directory, f"dump_{i}.csv")

                with open(csv_filename, 'w', newline='') as csv_file:
                    csv_file.write(csv_data)
                logging.info(f"CSV data saved to {csv_filename}")
            else:
                logging.error(
                    f"API request failed with \
                    status code {response.status_code}")
            sleep(2)

        # Invoke shared_task to merge data
        merge_data.delay()

    except requests.RequestException as e:
        logging.error(f"API request failed: {str(e)}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")


@shared_task
def transform_data(df, cols):
    try:
        new_data = df.copy()
        # Preprocess some columns
        new_data['acq_date'] = pd.to_datetime(
            new_data['acq_date']).astype('datetime64[us]')
        # new_data['hour'] = new_data['acq_time'].apply(parse_time)
        # new_data['hour'] = new_data['hour'].dt.components.hours

        logging.info(f"Transform Hour: Done. Shape {new_data.shape}")

        new_data.columns = cols

        return new_data
    except Exception as e:
        logging.error(f"Error preprocessing new data {str(e)}")


@shared_task
def filter_by_area(
        points_df,
        polygons_df,
        lat_col='latitude',
        lon_col='longitude'):
    points_gdf = gpd.GeoDataFrame(
            points_df,
            geometry=gpd.points_from_xy(
                points_df[lat_col],
                points_df[lon_col])
            )

    # Return the points that are not in the areas to ignore
    filtered_points = points_gdf[
            ~(points_gdf.within(polygons_df.unary_union))]
    return points_df[points_df.index.isin(filtered_points.index)]


@shared_task
def merge_data():
    BASE_DIR = settings.BASE_DIR

    try:
        default_cols = ['latitude', 'longitude', 'brightness', 'scan',
                        'track', 'acq_date', 'acq_time',
                        'satellite', 'instrument', 'confidence', 'version',
                        'bright_t31', 'frp', 'daynight']
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
                    f"Columns do not match. Expected {len(default_cols)}, \
                    got {len(new_data.columns)}")
                continue

            new_data_transformed = transform_data.delay(
                    new_data,
                    db.columns
                    ).get()

            merged_data = pd.concat(
                [merged_data, new_data_transformed], axis=0)

            logging.info(f"Concatenate: Done. Shape {merged_data.shape}")

            os.remove(csv_filename)
            logging.info(f"Successfully removed file: {csv_filename}")

        # Drop duplicates
        # merged_data.drop_duplicates(inplace=True)
        # merged_data.reset_index(drop=True, inplace=True)
        # logging.info(f"Drop Duplicates: Done. Shape {merged_data.shape}")

        # Filter Volcanoes and Static data like solar panels from data

        # Read areas for point filtering
        geojson_path = os.path.join(BASE_DIR, 'data/ignore_areas.geojson')

        try:
            before_size = merged_data.shape[0]
            gdf_areas = gpd.read_file(geojson_path)

            merged_data = filter_by_area.delay(merged_data, gdf_areas).get()

            after_size = merged_data.shape[0]
            logging.info(f"Filtered points from {before_size} to {after_size}")
        except Exception as e:
            return logging.error(f"Error in filtering points by area: \
                    {str(e)}")

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

        gdf_comunas = gpd.read_file(comunas_path)

        merged_data['comuna'] = merged_data.apply(
                tag_comuna, axis=1, args=(gdf_comunas,))

        # TODO: Classify data with xgboost model to predict type.
        # TODO: Filter non-wildfire data (aka static data, volcanoes, etc).

        # Save to csv
        csv_filename = os.path.join(output_directory, "dump.csv")
        merged_data.to_csv(csv_filename, index=False)
        logging.info(f"Saving to csv: {csv_filename}")

        # Insert data into the database
        insert_data.delay()

    except FileNotFoundError:
        logging.error(f"The file {csv_filename} does not exist.")
    except PermissionError:
        logging.error(
            f"You don't have permission to delete the file {csv_filename}.")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")


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

            logging.info(f"Rows to insert {df.shape[0]}")

            if df.shape[0] == 0:
                logging.info("No new data to insert.")
                return

            wildfires_list = []

            for index, row in df.iterrows():

                if Wildfires.objects.filter(
                        latitude=row['latitude'],
                        longitude=row['longitude'],
                        acq_date=row['acq_date'],
                        acq_time=row['acq_time']
                        ) .exists():
                    continue

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
                    # type
                    comuna=row['comuna']
                )
                wildfires_list.append(wildfire)

            logging.info(f"Rows to insert after filtering \
                    {len(wildfires_list)}")
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
