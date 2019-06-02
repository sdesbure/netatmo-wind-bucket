import os
import time
import logging
from datetime import datetime
import json
import requests
from pathlib import Path

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

username = os.environ.get('NETATMO_USERNAME')
password = os.environ.get('NETATMO_PASSWORD')
client_id = os.environ.get('NETATMO_CLIENT_ID')
client_secret = os.environ.get('NETATMO_CLIENT_SECRET')
device_id = os.environ.get('NETATMO_DEVICE_ID')

if not username:
    logging.error("we need 'NETATMO_USERNAME' environment variable to run")
    exit(1)

if not password:
    logging.error("we need 'NETATMO_PASSWORD' environment variable to run")
    exit(1)

if not client_id:
    logging.error("we need 'NETATMO_CLIENT_ID' environment variable to run")
    exit(1)

if not client_secret:
    logging.error("we need 'NETATMO_CLIENT_SECRET' environment variable to run")
    exit(1)

if not device_id:
    logging.error("we need 'NETATMO_DEVICE_ID' environment variable to run")
    exit(1)

buckets_file = Path('buckets.json')
buckets = {"0": 0, "1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0, "8": 0, "9": 0}
last_time = 0
if buckets_file.is_file():
    logging.info("file for buckets exists, loading")
    with buckets_file.open() as json_file:
        try:
            data = json.load(json_file)
            buckets = data["buckets"]
            last_time = data["last_time"]
        except json.decoder.JSONDecodeError:
            logging.warn("buckets.json is not a valid json file, ignoring")
        except KeyError:
            logging.warn("buckets.json has no 'last_time' or 'buckets' key, ignoring")

def authenticate():
    payload = {'grant_type': 'password',
               'username': username,
               'password': password,
               'client_id': client_id,
               'client_secret': client_secret,
               'scope': 'read_station'}
    try:
        response = requests.post("https://api.netatmo.com/oauth2/token", data=payload)
        response.raise_for_status()
        access_token=response.json()["access_token"]
        logging.info("authenticated")
        return access_token
    except requests.exceptions.HTTPError as error:
        logging.error('%s: %s', error.response.status_code, error.response.text)
        exit(1)

def get_wind(access_token):
    params = {
        'access_token': access_token,
        'device_id': device_id
    }

    try:
        response = requests.post("https://api.netatmo.com/api/getstationsdata", params=params)
        response.raise_for_status()
        data = response.json()["body"]
        devices = data["devices"]
        for device in devices:
            modules = device["modules"]
            for module in modules:
                if "Wind" in module["data_type"]:
                    measurement_date = module["dashboard_data"]["time_utc"]
                    wind_speed = module["dashboard_data"]["WindStrength"]
                    return (measurement_date, wind_speed)
    except requests.exceptions.HTTPError as error:
        logging.error('%s: %s', error.response.status_code, error.response.text)
        exit(1)

def update_buckets(buckets, value):
    for speed, items in buckets.items():
        if int(speed) - value < 1:
            logging.info("value put in %s bucket (m/s)", speed)
            buckets[speed] += 1
            break
    return buckets

if __name__ == '__main__':
    while True:
        measurement_date, wind_speed = get_wind(authenticate())
        logging.info("time of measurement (utc): %s", datetime.fromtimestamp(measurement_date))
        logging.info("wind speed (km/h): %s", wind_speed)
        logging.info("wind speed (m/s): %s", int(wind_speed) * 0.27778)
        if measurement_date > last_time:
            buckets = update_buckets(buckets, int(wind_speed) * 0.27778)
            last_time = measurement_date
            with buckets_file.open(mode='w') as json_file:
                json.dump({'buckets': buckets, 'last_time': last_time}, json_file)
        time.sleep(600)
