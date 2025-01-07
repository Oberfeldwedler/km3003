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
    
    def getConnectionState(self) -> bool:
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
    
    def getConnectionState(self) -> bool:
        return "up"
    
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


    """
    This function configures the serial connection, using the
    settings in the dictionary supplied on initialization.
    The serial connection is not opened here.

    Args: 
        None
    Returns:
        ser: The configured serial connection as an object.
    """
    def __constructSerialConnection(self):
        ser = serial.serial_for_url(self.settings['port'], do_not_open=True)
        ser.baudrate = int(self.settings['baudrate'])
        ser.bytesize = int(self.settings['bytesize'])
        ser.parity = self.settings['parity']
        ser.stopbits = int(self.settings['stopbits'])
        ser.timeout = None
        return ser

    """
    This function opens the serial connection.
    After successfully opening the connection, __connectionState 
    is set to "up" and the callback function is executed.
    In case of an exception, the function sleeps, to limit 
    connection attempts to one per second.

    Args: 
        None
    Returns:
        None
    """
    def __openSerialConnection(self):
        try:
            self.ser = self.__constructSerialConnection()
            self.ser.open()
            self.__connectionState = "up"
            self.__scannerStateChangeCallback(self.__connectionState)
        except:
            self.__connectionState = "down"
            logging.debug("Connection to serial device could not be opened! Ignoring!")
            time.sleep(1)
            pass
 
    """
    This Function tries to read a line from the 
    scanner while no stop is requested. As long
    as there is no input from the scanner, 
    self.ser.readline() is blocking.
    In case self.ser.readline() throws an 
    exception, the __connectionState is set to down
    and the callback function is executed.

    Args: 
        None
    Returns:
        None
    """
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
            else:
                self.__openSerialConnection()
                
    """
    This Function checks whether there are elements in the queue.
    In case there are, it fetches the oldest element and returns it.
    In case there are none, None is returned.

    Args: 
        None
    Returns:
        item:
            String containing the value of a scanned barcode.
    """
    def getBarcode(self):
        if self.queue.empty() == False:
            item = self.queue.get(block=True)
        else:
            item = None
        return item
    
    def getConnectionState(self) -> bool:
        return self.__connectionState
    
    def close(self):
        self.isStopRequested = True
        self.ser.close()
