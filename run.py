import os
import time

import requests
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from requests_futures.sessions import FuturesSession
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

load_dotenv()

# Load environment variables
INFLUX_URL = os.environ.get("INFLUXDB_URL")
URL = os.environ.get("DEVICE_API_URL")
AUTH = os.environ.get("AUTH")
DEVICE = os.environ.get("DEVICE_ID")
PLUGS_LOCAL = os.environ.get("PLUG_URL")

# InfluxDB options
client = InfluxDBClient(url=INFLUX_URL, org="BStuff")
write_api = client.write_api(write_options=SYNCHRONOUS)
bucket = "tempHum"
# create a template point with the common tags and fields
point_template = (
    lambda name: Point(name).tag("temp", "room").field("temperature", None).field("humidity", None)
)("roomTempHum")


def write_data(temperature, humidity):
    # create a new point based on the template point, with the current temperature and humidity values
    point = point_template.field("temperature", temperature).field("humidity", humidity)
    # write the point to the bucket
    write_api.write(bucket=bucket, record=point)


def read_status():
    """Get status of the dehumidifier"""
    res = requests.get(url=PLUGS_LOCAL)
    json_res = res.json()
    dehum_status = json_res['ison']
    return dehum_status


def toggle_status(status):
    """Toggle status of the dehumidifier"""
    data = 'turn=on' if not status else 'turn=off'
    res = requests.post(url=PLUGS_LOCAL, data=data)


# create a session with a connection pool and retries
session = FuturesSession(max_workers=10)
session.mount('http://', HTTPAdapter(max_retries=3))


def read_temp_hum():
    while True:
        try:
            # make a request to the Shelly Cloud API for temperature and humidity data
            future = session.post(url=URL, data={'auth_key': AUTH, 'id': DEVICE})
            # get the response from the future
            response = future.result()
            # process the response if it is successful
            if response.status_code == 200:
                json_data = response.json()
                hum = float(json_data['data']['device_status']['humidity:0']['rh'])
                temp = float(json_data['data']['device_status']['temperature:0']['tC'])
                write_data(temp, hum)
                is_dehum_on = read_status()
                if hum <= 45 and is_dehum_on:
                    toggle_status(False)
                elif hum > 45 and not is_dehum_on:
                    toggle_status(True)
            # handle HTTP errors
            else:
                print(f'HTTP Error: {response.status_code}')
        except requests.RequestException as e:
            print(e)
        # measure the elapsed time and adjust the delay accordingly
        start_time = time.perf_counter()
        elapsed_time = time.perf_counter() - start_time
        delay = max(3 - elapsed_time, 0)
        time.sleep(delay)


if __name__ == '__main__':
    read_temp_hum()