import os
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import time
from barixSerial import pySerialComm
from dotenv import load_dotenv
import requests

load_dotenv()
#dotenv variables
influxUrl = os.getenv('LOCALURL')
url = os.getenv('URL')
auth = os.getenv('AUTH')
device = os.getenv('DEVICE')
data = {'auth_key': auth, 'id': device}

def writeData(temperature, humidity): # writes data to InfluxDB
    bucket = "tempHum"
    client = InfluxDBClient(url=influxUrl, org="BStuff")
    write_api = client.write_api(write_options=SYNCHRONOUS)
    p = Point("roomTempHum").tag("temp", "room").field(
        "temperature", temperature).field("humidity", humidity)
    write_api.write(bucket=bucket, record=p)

def requestApi(): #requests Shelly Cloud API sensor data (reports every 5 seconds)
    while True:
      response = requests.post(url=url, data=data)
      if response.status_code == 200:
          jsonData = response.json()
          hum = jsonData['data']['device_status']['humidity:0']['rh']
          temp = jsonData['data']['device_status']['temperature:0']['tC']
          fTemp = float(temp)
          fHum = float(hum)
          writeData(fTemp, fHum)
          time.sleep(5)
      elif response.status_code == 404:
          print('Not Found.')

requestApi()
