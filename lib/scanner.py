import queue
import serial
import threading

class Scanner():
    def __init__(self, serialSettingsDict):
        self.q = queue.Queue()
        ser = serial.serial_for_url(serialSettingsDict['port'], do_not_open=True)
        ser.baudrate = int(serialSettingsDict['baudrate'])
        ser.bytesize = int(serialSettingsDict['bytesize'])
        ser.parity = serialSettingsDict['parity']
        ser.stopbits = int(serialSettingsDict['stopbits'])
        ser.timeout = None
        ser.open()

        x = threading.Thread(target=self.__readFromScanner, args=(q, ser), daemon=True)
        x.start()

    def __readFromScanner(self):
        while True:
            self.q.put(self.ser.readline(), block=True, timeout=None)


    def getBarcode(self):
        if self.q.empty() == False:
            try: 
                item = self.q.get(block=True, timeout=0.05)
            except:
                item = None
        else:
            item = None
        return item

