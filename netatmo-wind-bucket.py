import os
import time
import logging
import datetime
import requests

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

if __name__ == '__main__':
    while True:
        measurement_date, wind_speed = get_wind(authenticate())
        logging.info("time of measurement (utc): %s", datetime.datetime.fromtimestamp(measurement_date))
        logging.info("wind speed (km/h): %s", wind_speed)
        time.sleep(600)
