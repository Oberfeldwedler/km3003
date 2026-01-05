import time
import serial
import threading

import logging

logger = logging.getLogger(__name__)

class Scanner():
    
    def __init__(self, settings: dict) -> None:
        self.settings = settings
   
    def getConnectionState(self) -> bool:
        pass

    def close(self) -> None:
        pass

class ConsoleScanner(Scanner):
    def __init__(self, settings: dict, barcodeScannedCallback) -> None:
        super().__init__(settings)
        self.__barcodeScannedCallback = barcodeScannedCallback
        self.thread = threading.Thread(target=self.__readFromScanner, daemon=True)
        self.isStopRequested = False
        self.thread.start()
 
    def __readFromScanner(self):
        while not self.isStopRequested:
            try:
                line = input()
                if line:
                    self.__barcodeScannedCallback(line)
            except Exception as e:
                logger.error("Cannot read from console!")
                logger.error(e)
                time.sleep(0.1)

    def getConnectionState(self) -> bool:
        return "up"
    
    def close(self) -> None:
        self.isStopRequested = True

class SerialScanner(Scanner):

    def __init__(self, serialSettingsDict, scannerStateChangeCallback, barcodeScannedCallback):
        super().__init__(serialSettingsDict)
        self.__scannerStateChangeCallback = scannerStateChangeCallback
        self.__barcodeScannedCallback = barcodeScannedCallback
        self.__connectionState = "never"

        self.thread = threading.Thread(target=self.__readFromScanner, daemon=True)
        self.isStopRequested = False
        self.thread.start()


    """
    This function configures the serial connection, using the settings in the dictionary supplied on initialization.
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
    After successfully opening the connection, __connectionState is set to "up" and the callback function is executed.
    In case of an exception, the function sleeps, to limit connection attempts to one per second.

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
            logger.info("Connection to scanner established.")
            self.__scannerStateChangeCallback(self.__connectionState)
        except Exception as e:
            self.__connectionState = "down"
            # Change to logger.error or logger.warning to see why it failed
            logger.error(f"Connection failed: {e}") 
            time.sleep(1)
 
    """
    This Function tries to read a line from the scanner while no stop is requested. 
    As long as there is no input from the scanner, self.ser.readline() is blocking.
    In case self.ser.readline() throws an exception, the __connectionState is set to down and the callback function is executed.

    Args: 
        None
    Returns:
        None
    """
    def __readFromScanner(self):
        while not self.isStopRequested:
            if self.__connectionState == "up":
                try:
                    line = self.ser.readline().decode().strip()
                    if line:
                        self.__barcodeScannedCallback(line)
                except Exception as e:
                    logger.error(f"Cannot read from serial device!")
                    logger.error(e)
                    self.__connectionState = "down"
                    self.__scannerStateChangeCallback(self.__connectionState)
            else:
                self.__openSerialConnection()
    
    def getConnectionState(self) -> bool:
        return self.__connectionState
    
    def close(self):
        self.isStopRequested = True
        self.ser.close()
