"""
    Executed daily by cron job. Will call the NASA FIRMS API with yesterday's date until now, or last seen max date.
"""

import os
import sys
import logging
import pandas as pd
import requests
import configparser
from datetime import datetime, timedelta
from config_loader import load_config, load_secrets

api_src = os.environ.get('API_SRC')
log_file = api_src + '/cron/logs/get-data.log'
logging.basicConfig(filename=log_file, encoding='utf-8', level=logging.INFO)

"""
    call_api_and_save_csv
        1) Load API key.
        2) NASA API request, it will fail sometimes due to limited requests/time.
        3) Save file to tmp.
"""

def call_api_and_save_csv(starting_date = None):
    try:
        # Load config
        config = load_config()
        secrets = load_secrets()

        base_url = config.get('API', 'base_url')
        api_key = secrets.get('Secrets', 'api_key')
        db_path = config.get('Database', 'db_path')

        # date - 1 day so it gets all the data in case it's processing today's data.
        current_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

        if os.path.exists(db_path):
            db = pd.read_parquet(db_path)
            db['acq_date'] = pd.to_datetime(db['acq_date'])
            max_date = db['acq_date'].max()
            current_date = (max_date - timedelta(days=1)).strftime('%Y-%m-%d')

        if starting_date:
            date_format = '%Y-%m-%d'
            parsed_date = datetime.strptime(starting_date, date_format)
            current_date = (parsed_date - timedelta(days=1)).strftime('%Y-%m-%d')

        logging.info(f"Requesting data with the following parameters Date={current_date}")

        api_url = config.get('API', 'api_template').format(api_key=api_key, date=current_date)
        output_directory = config.get('File', 'output_directory')
        request_url = base_url + api_url

        # Get & save data
        response = requests.get(request_url)

        if response.status_code == 200:
            csv_data = response.text

            if csv_data == 'Invalid MAP_KEY.':
                return logging.info(f"{csv_data} -> Probably too many requests.")

            csv_filename = os.path.join(output_directory, f"dump.csv")

            with open(csv_filename, 'w', newline='') as csv_file:
                csv_file.write(csv_data)
            logging.info(f"CSV data saved to {csv_filename}")
        else:
            logging.error(f"API request failed with status code {response.status_code}")

    except configparser.Error as e:
        logging.error(f"Error reading configuration: {str(e)}")
    except requests.RequestException as e:
        logging.error(f"API request failed: {str(e)}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    """
        Get data can be invoked with an starting date instead of now date or last max date..

        Consideration.
            1) This will not work with older data.
            2) To download old data, an archive download request is needed.

    """
    script_name = sys.argv[0]
    if len(sys.argv) == 2:
        datestr = sys.argv[1]
        call_api_and_save_csv(datestr)
    else:
        call_api_and_save_csv()