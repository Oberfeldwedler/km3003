import time
import queue
import serial
import threading



class Scanner():

    def __init__(self, serialSettingsDict):
        self.q = queue.Queue()
        self.ser = serial.serial_for_url(serialSettingsDict['port'], do_not_open=True)
        self.ser.baudrate = int(serialSettingsDict['baudrate'])
        self.ser.bytesize = int(serialSettingsDict['bytesize'])
        self.ser.parity = serialSettingsDict['parity']
        self.ser.stopbits = int(serialSettingsDict['stopbits'])
        self.ser.timeout = None
        self.ser.open()

        self.x = threading.Thread(target=self.__readFromScanner, daemon=True)
        self.x.start()
 
    def __readFromScanner(self):
        while True:
            try:
                line = self.ser.readline()
            except:
                print("Cannot read from scanner.")
                time.sleep(0.1)
            self.q.put(line, block=True, timeout=None)

    def getBarcode(self):
        if self.q.empty() == False:
            try: 
                item = self.q.get(block=True, timeout=0.05)
            except:
                item = None
        else:
            item = None
        return item
    
    def close(self):
        self.exit = True
        self.ser.close()
