import serial
import schedule
from barixSerial import pySerialComm

def wrSerial():
	schedule.run_pending()
	serial = pySerialComm()
	msg = serial.sendCommand(cmd='R01')
	temp, hum = msg.split(',')
	print(temp, hum)

schedule.every(1).seconds.do(wrSerial) #Runs the function every 1 seconds
