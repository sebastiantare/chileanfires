"""
    Executed daily by cron job. Will call the NASA FIRMS API with yesterday's date until now.
"""

import os
import logging
import requests
import configparser
from datetime import datetime, timedelta
from config_loader import load_config, load_secrets

logging.basicConfig(level=logging.INFO)

def call_api_and_save_csv():
    try:
        # Load config
        config = load_config()
        secrets = load_secrets()

        base_url = config.get('API', 'base_url')
        api_key = secrets.get('Secrets', 'api_key')
        current_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        api_url = config.get('API', 'api_template').format(api_key=api_key, date=current_date)
        output_directory = config.get('File', 'output_directory')
        request_url = base_url + api_url

        # Get & save data
        response = requests.get(request_url)

        if response.status_code == 200:
            csv_data = response.text

            if csv_data == 'Invalid MAP_KEY.':
                return logging.info(f"{csv_data}, probably too many requests.")

            csv_filename = os.path.join(output_directory, f"api_data_{current_date}.csv")

            with open(csv_filename, 'w', newline='') as csv_file:
                csv_file.write(csv_data)

            logging.info(f"CSV data saved to {csv_filename}")

        else:
            logging.info(f"API request failed with status code {response.status_code}")

    except configparser.Error as e:
        logging.error(f"Error reading configuration: {str(e)}")
    except requests.RequestException as e:
        logging.error(f"API request failed: {str(e)}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    call_api_and_save_csv()