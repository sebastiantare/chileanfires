"""
    Executed after the get-data.py, will merge the downloaded data with the existing csv file ensuring no duplicates.
"""

import os
import logging
import pandas as pd
from datetime import datetime, timedelta
from config_loader import load_config, load_secrets

logging.basicConfig(level=logging.INFO)

def call_api_and_save_csv():
    try:
        config = load_config()
        secrets = load_secrets()

        # Load files
        output_directory = config.get('File', 'output_directory')
        db_path = config.get('Database', 'db_path')

        current_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        csv_filename = os.path.join(output_directory, f"api_data_{current_date}.csv")
        new_data = pd.read_csv(csv_filename)

        if os.path.exists(db_path):
            db = pd.read_csv(db_path)
        else:
            db = pd.DataFrame(columns=new_data.columns)

        db.set_index(["acq_date", "acq_time"], inplace=True)
        new_data.set_index(["acq_date", "acq_time"], inplace=True)

        db.sort_values(["acq_date", "acq_time"], inplace=True)
        new_data.sort_values(["acq_date", "acq_time"], inplace=True)

        # Merge files with the updated data
        merged_data = pd.concat([db, new_data]).drop_duplicates()

        merged_data.reset_index(inplace=True)

        columns = [
            "country_id", "latitude", "longitude", "bright_ti4", "scan",
            "track", "acq_date", "acq_time", "satellite", "instrument",
            "confidence", "version", "bright_ti5", "frp", "daynight"
        ]

        merged_data = merged_data[columns]

        # Save DB csv file
        merged_data.to_csv(db_path, index=False)
        logging.info(f"Merged data saved to {db_path}")

    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")


if __name__ == "__main__":
    call_api_and_save_csv()
