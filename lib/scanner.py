import time
import queue
import serial
import threading

import logging

logger = logging.getLogger(__name__)

class Scanner():
    
    def __init__(self, settings: dict) -> None:
        self.settings = settings
        
    def getBarcode(self) -> str:
        raise NotImplementedError()

    def close(self) -> None:
        pass

class ConsoleScanner(Scanner):
    def __init__(self, settings: dict) -> None:
        super().__init__(settings)
        
        self.queue = queue.Queue()
        
        self.thread = threading.Thread(target=self.__readFromScanner, daemon=True)
        self.isStopRequested = False
        self.thread.start()
        
 
    def __readFromScanner(self):
        while not self.isStopRequested:
            try:
                line = input()
                self.queue.put(line, block=True, timeout=None)    
            except Exception as e:
                logger.error("Cannot read from console!")
                logger.error(e)
                time.sleep(0.1)

    
    def getBarcode(self) -> str:
        if self.queue.empty() == False:
            item = self.queue.get(block=True)
        else:
            item = None
        return item
    
    def close(self) -> None:
        self.isStopRequested = False

class SerialScanner(Scanner):

    def __init__(self, serialSettingsDict):
        super().__init__(serialSettingsDict)
        self.queue = queue.Queue()
        self.ser = serial.serial_for_url(serialSettingsDict['port'], do_not_open=True)
        self.ser.baudrate = int(serialSettingsDict['baudrate'])
        self.ser.bytesize = int(serialSettingsDict['bytesize'])
        self.ser.parity = serialSettingsDict['parity']
        self.ser.stopbits = int(serialSettingsDict['stopbits'])
        self.ser.timeout = None
        self.ser.open()
        
        self.thread = threading.Thread(target=self.__readFromScanner, daemon=True)
        self.isStopRequested = False
        self.thread.start()
        
 
    def __readFromScanner(self):
        while not self.isStopRequested:
            try:
                line = self.ser.readline().decode()
                self.queue.put(line, block=True, timeout=None)
            except Exception as e:
                logger.error(f"Cannot read from serial device!")
                logger.error(e)
                time.sleep(0.1)

    def getBarcode(self):
        if self.queue.empty() == False:
            item = self.queue.get(block=True)
        else:
            item = None
        return item
    
    def close(self):
        self.isStopRequested = True
        self.ser.close()
