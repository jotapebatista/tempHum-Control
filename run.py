from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import requests
import serial
import random
import schedule
import time

bucket = "tempHum"

client = InfluxDBClient(url="http://192.168.30.103:8086", org="BStuff")
write_api = client.write_api(write_options=SYNCHRONOUS)

def writeData():
  temp = random.randrange(14,36)
  hum = random.randrange(20,80,10)
  p = Point("roomTempHum").tag("temp", "room").field("temperature", temp).field("humidity", hum)
  print(p, temp, hum)
  write_api.write(bucket=bucket, record=p)

schedule.every(3).seconds.do(writeData)

while 1:
   schedule.run_pending()
   time.sleep(1)

'''
headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
}

params = {
    'db': 'tempHum',
}

data = 'roomTemp,temp=24 hum=46'
response = requests.post('http://192.168.30.103:8086/write', params=params, headers=headers, data=data)
print("{} {}".format(data, response))
'''