import serial
import schedule
from barixSerial import pySerialComm

msg = ''
char = serial.read(1).decode('utf-8')
print(char)
