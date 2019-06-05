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

MAX_RETRY = 10
RETRY_SLEEP = 60
SLEEP = 600

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
            logging.info("buckets: %s", buckets)
            logging.info("last_time: %s", last_time)
        except json.decoder.JSONDecodeError:
            logging.warn("buckets.json is not a valid json file, ignoring")
        except KeyError:
            logging.warn("buckets.json has no 'last_time' or 'buckets' key, ignoring")

def post_and_get_json(url, key, data=None, params=None):
    try:
        response = requests.post(url, params=params, data=data)
        response.raise_for_status()
        return response.json()[key]
    except requests.exceptions.HTTPError as error:
        logging.error('%s: %s', error.response.status_code, error.response.text)
        return None

def authenticate():
    payload = {'grant_type': 'password',
               'username': username,
               'password': password,
               'client_id': client_id,
               'client_secret': client_secret,
               'scope': 'read_station'}
    return post_and_get_json("https://api.netatmo.com/oauth2/token", "access_token", data=payload)

def get_wind(access_token):
    params = {
        'access_token': access_token,
        'device_id': device_id
    }
    data = post_and_get_json("https://api.netatmo.com/api/getstationsdata", "body", params=params)
    if data:
        return parse_devices(data["devices"])
    else:
        return None, None

def parse_devices(devices):
    for device in devices:
        date, speed = parse_modules(device["modules"])
        if date:
            return date, speed
    return None, None

def parse_modules(modules):
    for module in modules:
        date, speed = parse_module(module)
        if date:
            return date, speed
    return None, None

def parse_module(module):
    if "Wind" in module["data_type"]:
        measurement_date = module["dashboard_data"]["time_utc"]
        wind_speed = module["dashboard_data"]["WindStrength"]
        return measurement_date, wind_speed
    return None, None

def update_buckets(buckets, value):
    for speed, items in buckets.items():
        if value - int(speed) < 1:
            logging.info("value put in %s bucket (m/s)", speed)
            buckets[speed] += 1
            break
    return buckets

def retry_wait(retry, action):
    if retry < MAX_RETRY:
        logging.warn("Issue with %s, waiting %s seconds", action, RETRY_SLEEP)
        time.sleep(RETRY_SLEEP)
        retry += 1
    else:
        logging.error("too many issue with %s, waiting %s seconds", action, SLEEP)
        time.sleep(SLEEP)
    return retry

def parse_datas(retry, measurement_date, wind_speed):
    global last_time
    global buckets
    logging.info("time of measurement (utc): %s", datetime.fromtimestamp(measurement_date))
    logging.info("wind speed (km/h): %s", wind_speed)
    logging.info("wind speed (m/s): %s", int(wind_speed) * 0.27778)
    if measurement_date > last_time:
        buckets = update_buckets(buckets, int(wind_speed) * 0.27778)
        last_time = measurement_date
        with buckets_file.open(mode='w') as json_file:
            json.dump({'buckets': buckets, 'last_time': last_time}, json_file)
        time.sleep(SLEEP - (retry * RETRY_SLEEP))

def get_datas(retry, token):
    measurement_date, wind_speed = get_wind(token))
    if measurement_date:
        parse_datas(retry, measurement_date, wind_speed)
        retry = 0
    else: 
        retry = retry_wait(retry, "retrieving wind")

if __name__ == '__main__':
    retry = 0
    while True:
        token = authenticate()
        if token:
            retry = get_datas(retry, token)
        else:
            retry = retry_wait(retry, "authentication")
