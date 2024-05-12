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
    
    def isConnected(self) -> bool:
        pass

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
    
    def isConnected(self) -> bool:
        return True
    
    def close(self) -> None:
        self.isStopRequested = False

class SerialScanner(Scanner):

    def __init__(self, serialSettingsDict, scannerStateChangeCallback ):
        super().__init__(serialSettingsDict)
        self.queue = queue.Queue()
        self.__scannerStateChangeCallback = scannerStateChangeCallback
        self.__connectionState = "never"

        self.thread = threading.Thread(target=self.__readFromScanner, daemon=True)
        self.isStopRequested = False
        self.thread.start()

    def __constructSerialConnection(self):
        ser = serial.serial_for_url(self.settings['port'], do_not_open=True)
        ser.baudrate = int(self.settings['baudrate'])
        ser.bytesize = int(self.settings['bytesize'])
        ser.parity = self.settings['parity']
        ser.stopbits = int(self.settings['stopbits'])
        ser.timeout = None
        return ser
        
    def __openSerialConnection(self):
        try:
            self.ser = self.__constructSerialConnection()
            self.ser.open()
            self.__connectionState = "up"
            self.__scannerStateChangeCallback(self.__connectionState)
        except:
            self.__connectionState = "down"
            self.__scannerStateChangeCallback(self.__connectionState)
            logging.debug("Connection to serial device could not be opened! Ignoring!")
            time.sleep(1)
            pass
 
    def __readFromScanner(self):
        while not self.isStopRequested:
            if self.__connectionState == "up":
                try:
                    line = self.ser.readline().decode()
                    self.queue.put(line, block=True, timeout=None)
                except Exception as e:
                    logger.error(f"Cannot read from serial device!")
                    logger.error(e)
                    self.__connectionState = "down"
                    self.__scannerStateChangeCallback(self.__connectionState)
                    pass
            else:
                self.__openSerialConnection()
                

    def getBarcode(self):
        if self.queue.empty() == False:
            item = self.queue.get(block=True)
        else:
            item = None
        return item
    
    def isConnected(self) -> bool:
        return self.__connectionActive
    
    def close(self):
        self.isStopRequested = True
        self.ser.close()
