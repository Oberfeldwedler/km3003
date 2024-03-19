import queue
import serial
import threading

class Scanner():
    def __init__(self, serialSettingsDict):
        self.q = queue.Queue()
        # TODO
        # Make parity and other serial setting configurable
        self.ser = serial.Serial( serialSettingsDict['port'], serialSettingsDict['baudrate'], timeout=None, parity=serial.PARITY_EVEN) 
        x = threading.Thread(target=self.__readFromScanner, args=(q, ser), daemon=True)
        x.start()

    def __readFromScanner(self, q, ser):
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
            
