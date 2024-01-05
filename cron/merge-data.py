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
        new_data['acq_date'] = pd.to_datetime(new_data['acq_date']).astype('datetime64[us]')
        new_data['hour'] = new_data['acq_time'].apply(parse_time)
        new_data['hour'] = new_data['hour'].dt.components.hours

        logging.info(f"Transform Hour: Done. Shape {new_data.shape}")

        # Drop and order columns
        new_data = new_data[cols]
        logging.info(f"Filter Columns: Done. Shape {new_data.shape}")

        # Remove low confidence data
        new_data = new_data[~(new_data['confidence'] == 'l')]
        logging.info(f"Filter low confidence: Done. Shape {new_data.shape}")

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
        logging.info(f"New Data Size {new_data.shape}")

        if os.path.exists(db_path):
            db = pd.read_parquet(db_path)
        old_len = len(db)

        logging.info(f"DB Data Size {db.shape}")

        # Transform new data to match db format
        new_data_transformed = transformData(new_data, db.columns)

        if not db.columns.equals(new_data_transformed.columns):
            logging.error("Columns of DataFrames do not match. Aborting concatenation.")
            return

        # Merge db with the new data
        logging.info(f"Concatenating: {db.shape} and {new_data_transformed.shape}")
        merged_data = pd.concat([db, new_data_transformed], axis=0)

        logging.info(f"Removing duplicates.")
        merged_data.drop_duplicates(inplace=True)

        logging.info(f"Merged Data Size {len(merged_data)}")

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
