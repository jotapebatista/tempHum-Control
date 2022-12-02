from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import time
from barixSerial import pySerialComm

def writeData(temperature, humidity):
  bucket = "tempHum"
  client = InfluxDBClient(url="http://192.168.30.103:8086", org="BStuff")
  write_api = client.write_api(write_options=SYNCHRONOUS)
  p = Point("roomTempHum").tag("temp", "room").field(
      "temperature", temperature).field("humidity", humidity)
  print(p, temperature, humidity)
  write_api.write(bucket=bucket, record=p)

def wrSerial():
  print('#1')
  while 1:
    serial = pySerialComm()
    msg = serial.sendCommand(cmd='R01')
    temp, hum = msg.split(',')
    writeData(int(temp), int(hum))
    time.sleep(2)

wrSerial()
