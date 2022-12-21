import os
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import time
from dotenv import load_dotenv
import requests
from requests.adapters import HTTPAdapter
from requests_futures.sessions import FuturesSession

load_dotenv()
# dotenv variables (so it's not exposed on github)
influxUrl = os.getenv('LOCALURL')
url = os.getenv('URL')
auth = os.getenv('AUTH')
device = os.getenv('DEVICE')
data = {'auth_key': auth, 'id': device}
plugSURL = os.getenv('PLUGSLOCAL')

# InfluxDB options
client = InfluxDBClient(url=influxUrl, org="BStuff")
write_api = client.write_api(write_options=SYNCHRONOUS)
bucket = "tempHum"
# create a template point with the common tags and fields
point_template = Point("roomTempHum").tag("temp", "room").field(
    "temperature", None).field("humidity", None)

def writeData(temperature, humidity):  # writes data to influxDB
    # create a new point based on the template point, with the current temperature and humidity values
    point = point_template.field(
        "temperature", temperature).field("humidity", humidity)
    # write the point to the bucket
    write_api.write(bucket=bucket, record=point)

def readStatus():  # get status of the dehumidifier
    res = requests.get(url=plugSURL)
    jsonRes = res.json()
    dehumStatus = jsonRes['ison']
    return dehumStatus
 
def toggleStatus(status):  # toggle status of the dehumidifier
    if status == True:
        res = requests.post(url=plugSURL, data='turn=on')
    else:
        res = requests.post(url=plugSURL, data='turn=off')

# create a session with a connection pool and retries
session = FuturesSession(max_workers=10)
session.mount('http://', HTTPAdapter(max_retries=3))

def readTempHum():
    while True:
        try:
            # make a request to the Shelly Cloud API for temperature and humidity data
            future = session.post(url=url, data=data)
            # get the response from the future
            response = future.result()
            # process the response if it is successful
            if response.status_code == 200:
                jsonData = response.json()
                hum = float(jsonData['data']['device_status']['humidity:0']['rh'])
                temp = float(jsonData['data']['device_status']['temperature:0']['tC'])
                writeData(temp, hum)
                isDehumOn = readStatus()
                if hum <= 45 and isDehumOn:
                    toggleStatus(False)
                elif hum > 45 and not isDehumOn:
                    toggleStatus(True)
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

readTempHum()