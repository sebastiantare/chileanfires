"""
    Executed after the get-data.py, will merge the downloaded data with the existing csv file ensuring no duplicates.
"""

import os
import sys
import logging
import pandas as pd
from datetime import datetime, timedelta
from config_loader import load_config, load_secrets

api_src = os.environ.get('API_SRC')
log_file = api_src + '/cron/logs/merge-data.log'
logging.basicConfig(filename=log_file, encoding='utf-8', level=logging.INFO)


def parse_time(value):
    hours = value // 100
    minutes = value % 100
    return pd.to_timedelta(f"{hours} hours {minutes} minutes")


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


"""
    call_api_and_save_csv
        1) Reads parquet db file and new data csv.
        2) Transforms new data to match db format.
        3) Drops duplicates.
        4) Concatenates them and make a new file.
        5) Uses the new file to insert data in PostgreSQL.
"""


def call_api_and_save_csv():
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
        output_directory = config.get('File', 'output_directory')
        django_directory = config.get('File', 'django_directory')

        merged_data = pd.DataFrame(columns=default_cols, dtype='object')

        for i in range(3):
            csv_filename = os.path.join(output_directory, f"dump_{i}.csv")
            new_data = pd.read_csv(csv_filename)
            logging.info(f"New Data Size {new_data.shape}")

            # Drop country
            new_data.drop('country_id', axis=1, inplace=True)

            # Transform new data to match db format
            new_data_transformed = transformData(new_data, db.columns)

            # Concat data
            merged_data = pd.concat([merged_data, new_data_transformed], axis=0)
            
            logging.info(f"Concatenate: Done. Shape {merged_data.shape}")

            os.remove(csv_filename)
            logging.info(f"Successfully removed file: {csv_filename}")

        # Drop duplicates
        #merged_data.drop_duplicates(inplace=True)
        #merged_data.reset_index(drop=True, inplace=True)
        logging.info(f"Drop Duplicates: Done. Shape {merged_data.shape}")

        # Save to csv
        csv_filename = os.path.join(django_directory, f"dump.csv")
        merged_data.to_csv(csv_filename, index=False)
        logging.info(f"Saving to csv: {csv_filename}")

    except FileNotFoundError:
        logging.error(f"The file {csv_filename} does not exist.")
    except PermissionError:
        logging.error(
            f"You don't have permission to delete the file {csv_filename}.")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    call_api_and_save_csv()
