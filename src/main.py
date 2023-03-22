import os
import time
import logging.config
import requests
import json
from requests.adapters import HTTPAdapter
from requests_futures.sessions import FuturesSession
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS


# Load configuration settings
CONFIG_FILE = "config/config.json"
with open(CONFIG_FILE, "r") as config_file:
    config = json.load(config_file)

# Setup logging
LOG_FILE = "logs/app.log"
logging.config.dictConfig({
    "version": 1,
    "handlers": {
        "file_handler": {
            "class": "logging.FileHandler",
            "filename": LOG_FILE,
            "formatter": "log_formatter"
        }
    },
    "loggers": {
        "": {
            "level": "INFO",
            "handlers": ["file_handler"]
        }
    },
    "formatters": {
        "log_formatter": {
            "format": "%(asctime)s [%(levelname)-5.5s] %(message)s"
        }
    }
})
logger = logging.getLogger(__name__)

# InfluxDB options
bucket = config["influxdb"]["bucket"]
client = InfluxDBClient(url=config["influxdb"]["url"], org=config["influxdb"]["org"])
write_api = client.write_api(write_options=SYNCHRONOUS)

# Device options
device_url = config["device"]["api_url"]
device_auth = config["device"]["auth_key"]
device_id = config["device"]["id"]

# Plug options
plug_url = config["plug"]["url"]


def write_data(temperature, humidity):
    """Write temperature and humidity data to InfluxDB."""
    point = Point("roomTempHum").tag("temp", "room").field("temperature", temperature).field("humidity", humidity)
    write_api.write(bucket=bucket, record=point)


def read_status():
    """Get status of the dehumidifier."""
    try:
        res = requests.get(url=plug_url)
        json_res = res.json()
        return json_res["ison"]
    except requests.RequestException:
        logger.exception("Error getting dehumidifier status")
        return False


def toggle_status(status):
    """Toggle status of the dehumidifier."""
    try:
        data = "turn=on" if not status else "turn=off"
        requests.post(url=plug_url, data=data)
    except requests.RequestException:
        logger.exception("Error toggling dehumidifier status")


# Create a session with a connection pool and retries
session = FuturesSession(max_workers=config["device"]["max_workers"])
session.mount("http://", HTTPAdapter(max_retries=config["device"]["max_retries"]))


def read_temp_hum():
    """Read temperature and humidity data from the device API."""
    while True:
        try:
            future = session.post(url=device_url, data={"auth_key": device_auth, "id": device_id})
            response = future.result()
            if response.status_code == 200:
                json_data = response.json()
                hum = float(json_data["data"]["device_status"]["humidity:0"]["rh"])
                temp = float(json_data["data"]["device_status"]["temperature:0"]["tC"])
                write_data(temp, hum)
                is_dehum_on = read_status()
                if hum <= config["device"]["humidity_threshold"] and is_dehum_on:
                    toggle_status(False)
                elif hum > config["device"]["humidity_threshold"] and not is_dehum_on:
                    toggle_status(True)
            else:
                logger.error(f"HTTP Error: {response.status_code}")
        except requests.RequestException:
            logger.exception("Error while making request to device API")

        time.sleep(config["device"]["delay"])


if __name__ == "__main__":
    logger.info("Starting Monitoring Service Application")
    read_temp_hum()