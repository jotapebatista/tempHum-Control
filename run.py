import requests
from datetime import datetime
import serial

headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
}

params = {
    'db': 'tempHum',
}

data = 'roomTemp temp=24'
response = requests.post('http://192.168.30.103:8086/write', params=params, headers=headers, data=data)