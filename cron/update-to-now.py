"""
    This script is run when initializing the repo, 
    will request all the missing data until now starting from the last achive datapoint.
"""

import os
import logging
import requests
import pandas as pd
from time import sleep
from datetime import datetime, timedelta
from config_loader import load_config, load_secrets
import subprocess

log_file = './logs/update-to_now.log'
logging.basicConfig(filename=log_file, encoding='utf-8', level=logging.INFO)

def getStartEndDate():
    config = load_config()

    db_path = config.get('Database', 'db_path')
    db = pd.read_parquet(db_path)
    db['acq_date'] = pd.to_datetime(db['acq_date'])
    max_date = db['acq_date'].max()

    start_date = max_date
    start_date = start_date.strftime('%Y-%m-%d') 

    end_date = datetime.now().strftime('%Y-%m-%d')

    logging.info(f"Getting data since {start_date} until {end_date}...")

    return start_date, end_date

def invokeGetDate(script_path = './get-data.py'):
    try:
        logging.info(f"Invoking get-data.py...")

        command = ["python", script_path]
        subprocess.run(command, check=True)
        logging.info(f"The script '{script_path}' has finished successfully.")

        logging.info(f"Invoking merge-data.py...")
        invokeMergeData()
    except subprocess.CalledProcessError as e:
        logging.error(f"Error while executing the script: {e}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")

def invokeMergeData(script_path = './merge-data.py'):
    try:
        command = ["python", script_path]
        subprocess.run(command, check=True)
        logging.info(f"The script '{script_path}' has finished successfully. {datetime.now()}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error while executing the script: {e}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")

def update_from_last_date():
    try:
        start_date, end_date = getStartEndDate()

        # Get new data until we reach today's date
        while start_date < end_date and start_date < datetime.now().strftime('%Y-%m-%d'):
            invokeGetDate()
            sleep(2)
            start_date, end_date = getStartEndDate()

        logging.info("Done...")

    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    update_from_last_date()

if __name__ == "__main__":
    update_from_last_date()