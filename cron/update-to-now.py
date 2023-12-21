"""
    This script is run when initializing the repo, will request all the missing data until now.
"""

import os
import logging
import requests
import pandas as pd
from time import sleep
from datetime import datetime, timedelta
from config_loader import load_config, load_secrets

logging.basicConfig(level=logging.INFO)

def update_from_last_date():
    try:
        # Load configs
        config = load_config()
        secrets = load_secrets()

        base_url = config.get('API', 'base_url')
        db_path = config.get('Database', 'db_path')
        api_key = secrets.get('Secrets', 'api_key')

        # Get max date to get new data
        db = pd.read_csv(db_path)
        max_date = db['acq_date'].max()
        start_date = datetime.strptime(max_date, '%Y-%m-%d')
        end_date = datetime.now()

        # Get new data until we reach now date
        while start_date <= end_date:
            current_date_str = start_date.strftime('%Y-%m-%d')

            api_url = config.get('API', 'api_template').format(api_key=api_key, date=current_date_str)
            request_url = base_url + api_url

            response = requests.get(request_url)

            if response.status_code == 200:
                csv_data = response.text

                if csv_data == 'Invalid MAP_KEY.':
                    logging.info(f"{csv_data}, probably too many requests. Waiting 10 seconds...")
                    sleep(10)
                    continue

                new_data = pd.read_csv(pd.compat.StringIO(csv_data))

                # Ensure 'acq_date' column is in datetime format
                new_data['acq_date'] = pd.to_datetime(new_data['acq_date'])

                # Get the new maximum date from the fetched data
                max_date_new_data = new_data['acq_date'].max()

                # Fetch new data for the next date range
                start_date = max_date_new_data + timedelta(days=1)

                # Merge new data with existing data without duplicates
                existing_db = pd.concat([existing_db, new_data]).drop_duplicates()

                logging.info(f"New data fetched and merged for date range: {current_date_str} - {max_date_new_data}")
            else:
                logging.error(f"API request failed with status code {response.status_code}")

        # Reset the index
        existing_db.reset_index(drop=True, inplace=True)

        # Save the merged data back to the database CSV
        existing_db.to_csv(db_path, index=False)

        logging.info(f"Final merged data saved to {db_path}")

    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    update_from_last_date()
