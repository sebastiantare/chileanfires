"""
    Executed after the get-data.py, will merge the downloaded data with the existing csv file ensuring no duplicates.
"""

import os
import sys
import logging
import pandas as pd
from datetime import datetime, timedelta
from config_loader import load_config, load_secrets

log_file = './logs/merge-data.log'
logging.basicConfig(filename=log_file, encoding='utf-8', level=logging.INFO)

def parse_time(value):
    hours = value // 100
    minutes = value % 100
    return pd.to_timedelta(f"{hours} hours {minutes} minutes")

def transformData(df, cols):
    try:
        new_data = df.copy()
        # Preprocess some columns
        new_data['acq_date'] = pd.to_datetime(new_data['acq_date'])
        new_data['hour'] = new_data['acq_time'].apply(parse_time)
        new_data['hour'] = new_data['hour'].dt.components.hours

        # Drop and order columns
        new_data = new_data[cols]
        # Remove low confidence data
        new_data = new_data[~(new_data['confidence'] == 'l')]

        return new_data
    except Exception as e:
        logging.error(f"Error preprocessing new data {str(e)}")

"""
    call_api_and_save_csv
        1) Reads parquet db file and new data csv.
        2) Transforms new data to match db format.
        3) Drops duplicates.
        4) Concatenates them and overwrites old db.
        5) Deletes new data csv.
"""
def call_api_and_save_csv():
    try:
        config = load_config()
        default_cols = ['latitude', 'longitude', 'scan', 'track', 'acq_date', 'acq_time', 'confidence', 'frp', 'daynight', 'hour']
        db = pd.DataFrame(columns=default_cols)

        # Load files
        output_directory = config.get('File', 'output_directory')
        db_path = config.get('Database', 'db_path')

        csv_filename = os.path.join(output_directory, f"dump.csv")

        new_data = pd.read_csv(csv_filename)

        if os.path.exists(db_path):
            db = pd.read_parquet(db_path)
        old_len = len(db)

        # Transform new data to match db format
        new_data = transformData(new_data, db.columns)

        # Merge db with the new data
        merged_data = pd.concat([db, new_data], axis=0).drop_duplicates()

        new_len = len(merged_data)

        # Save DB csv file
        merged_data.to_parquet(db_path, index=False)
        logging.info(f"DB successfully overwritten to {db_path} with {new_len-old_len} new datapoints added.")

        os.remove(csv_filename)
        logging.info(f"Successfully removed file: {csv_filename}")

    except FileNotFoundError:
        logging.error(f"The file {csv_filename} does not exist.")
    except PermissionError:
        logging.error(f"You don't have permission to delete the file {csv_filename}.")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    call_api_and_save_csv()