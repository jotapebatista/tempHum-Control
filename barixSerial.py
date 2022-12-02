import serial
import threading

class pySerialComm:
    LOCK = threading.Lock()

    def __init__(self, port='/dev/ttyACM0'):
        self.serial = serial.Serial(
            port, 115200, timeout=1.0, write_timeout=1.0)

    def sendCommand(self, cmd):
        with self.LOCK:
            cmd += '\r\n'
            self.serial.reset_input_buffer()
            self.serial.write(cmd.encode('utf-8'))

            msg = ''
            while True:
                try:
                    char = self.serial.read(1).decode('utf-8')
                    if len(char) != 1:
                        break
                    if char != '\n' and char != '\r':
                        msg += char
                    elif msg and char == '\n':
                        return msg
                except Exception as e:
                    break
