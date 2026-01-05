import pymysql.cursors
from decimal import Decimal
import threading
from lib import classes

import logging

logger = logging.getLogger(__name__)

class MySqlDataError(Exception):
    """Raised when data fetched from database is inconsistent."""

class MySql:
    def __init__(self, mySqlSettingsDict):
        self.lock = threading.RLock()
        self.__connectionState = "never"
        self.hostAddress = mySqlSettingsDict["host_address"]
        self.portNumber = int(mySqlSettingsDict["port_number"])
        self.username = mySqlSettingsDict["username"]
        self.password = mySqlSettingsDict["password"]
        self.database = mySqlSettingsDict["database"]
        self.connection = None  

    def getConnectionState(self):
        return self.__connectionState

    def establishConnection(self):
        with self.lock:
            try:
                logger.debug("Trying to connect to database:")
                logger.debug(f"HOST={self.hostAddress}:{self.portNumber}, USER={self.username}, DB={self.database}")
                self.connection = pymysql.connect(user=self.username, password=self.password,
                                        host=self.hostAddress, port=self.portNumber,
                                        database=self.database, 
                                        read_timeout=1, write_timeout=1, connect_timeout=1)
                self.dictCursor = self.connection.cursor(pymysql.cursors.DictCursor)
                self.__connectionState = "up"
                logger.info("Connection to database established.")
                return True
            except Exception as err:
                logger.error("Cannot connect to database!")
                logger.error(err)
                self.__connectionState= "down"
                return False
        
    def closeConnection(self):
        with self.lock:
            logger.info("Connection to database closed.")
            try:
                self.connection.close()
            except:
                logging.warning("Connection to database could not be closed! Ignoring!")
                pass

    """
    Checks whether there is a working database connection and reestablishes when there isn't.

    Args: 
        None
    Returns:
        connectionState: The connection state to the MySql server connectionStateChanged: 
        This indicates, whether the connection state is now different to the one specified in __connectionState.
        This information is used by the GUI to update the layout.
    """
    def ensureDatabaseConnection(self):
        with self.lock:
            lastConnectionState = self.__connectionState
            if self.connection == None:
                # Here we land only when the application has just been started and a database connection has not yet been established.
                # This is the regular way for connection to be established for the first time.
                self.establishConnection()
            else:
                try:
                    self.connection.ping(reconnect=True)
                    self.__connectionState = "up"
                except:
                    self.__connectionState = "down"

            if not self.__connectionState == lastConnectionState:
                connectionStateChanged = True
            else:
                connectionStateChanged = False

            return self.__connectionState, connectionStateChanged

    def __getUserFromDatabase(self, barcode):
        query = ("SELECT * FROM users WHERE id = (SELECT user_id FROM `user-barcodes` WHERE barcode=%s)")

        try:
            logger.debug(self.dictCursor.mogrify(query, ( barcode, ) ))
            self.dictCursor.execute(query, ( barcode, ) )
            rowCount = self.dictCursor.rowcount

            if rowCount == 1:
                dataDict = self.dictCursor.fetchone()
                return classes.User(
                    dataDict['id'], 
                    dataDict['first_name'], 
                    dataDict['last_name'], 
                    dataDict['emoji'], 
                    Decimal(dataDict['price_factor'])
                )
            elif rowCount > 1:
                logger.error(f"Barcode {barcode} does not identify a unique user! ({rowCount} results)")
            self.connection.commit()
        except MySqlDataError as err:
            self.connection.rollback()
            logger.error("Error during SELECT from table USER:")
            logger.error(err)
        except Exception as err:
            logger.error(err)
        return None
        
    def __getProductFromDatabase(self, barcode):
        query = ("SELECT * FROM products WHERE barcode=%s")
        
        try:
            logger.debug(self.dictCursor.mogrify(query, ( barcode, ) ))
            self.dictCursor.execute(query, ( barcode, ) )
            rowCount = self.dictCursor.rowcount
            
            if rowCount == 1:
                dataDict = self.dictCursor.fetchone()
                return classes.Product(
                    dataDict['id'], 
                    dataDict['name'], 
                    Decimal(dataDict['sell_price']), 
                    dataDict['brand']
                )
            elif rowCount > 1:
                logger.error(f"Barcode {barcode} does not identify a unique product! ({rowCount} results)")
            self.connection.commit()
        except MySqlDataError as err:
            logger.error("Error during SELECT from table USER")
            logger.error(err)
        except Exception as err:
            logger.error(err)
        return None


    """
    Searches in the database for users or products with the supplied barcode. 
    If an entity can be identified by the code, an object containing the fetched information about the entity is returned.

    Args: 
        barcode: The content of a scanned barcode.
    Returns:
        entity: Object representing a user or a product. 
            None if no matching entity is found in the database. 
    """
    def runBarcodeAgainstDatabase(self, barcode):
        with self.lock:
            user = self.__getUserFromDatabase(barcode)
            product = self.__getProductFromDatabase(barcode)
            
            if product != None and user == None:
                return product
            elif product == None and user != None:
                return user
            elif product != None and user != None:
                logger.error(f"Barcode {barcode} is both a user and product!")
                return None
            else:
                logger.warning(f"Barcode {barcode} is neither user nor product!")
                return None

    def calculateAndUpdateUserBalance(self, user):
        with self.lock:
            get_sum_purchases = ("SELECT SUM(price_then * price_factor_then) AS total_spent FROM purchases WHERE user_id = %s;")
            get_sum_deposits = ("SELECT SUM(amount) AS total_deposited FROM deposits WHERE user_id = %s;")
            update_balance = ("UPDATE users SET current_balance=%s WHERE (id=%s)")

            try:
                self.connection.begin()

                # logger.debug(self.dictCursor.mogrify(get_sum_purchases, ( user.id, )))
                self.dictCursor.execute(get_sum_purchases, ( user.id, ) ) 
                result_purchases = self.dictCursor.fetchone()
                # Handle case where SUM returns None (NULL)
                total_spent = Decimal(result_purchases['total_spent'] if result_purchases['total_spent'] else 0.0)

                # logger.debug(self.dictCursor.mogrify(get_sum_deposits, ( user.id, )))
                self.dictCursor.execute(get_sum_deposits, ( user.id, ) )
                result_deposits = self.dictCursor.fetchone()
                # Handle case where SUM returns None (NULL)
                total_deposited = Decimal(result_deposits['total_deposited'] if result_deposits['total_deposited'] else 0.0)

                new_balance = total_deposited -  total_spent
                new_balance = new_balance.quantize(Decimal('0.01'))

                # logger.debug(self.dictCursor.mogrify(update_balance_query, (new_balance, user.id)))
                self.dictCursor.execute(update_balance, ( new_balance, user.id ) )

                self.connection.commit()

                return new_balance
                    
            except Exception as err:
                self.connection.rollback()
                logger.error("Failed to recalculate and update user balance:")
                logger.error(err)
                return None

    def insertCheckout(self, products_list, user):
        with self.lock:
            new_balance = self.calculateAndUpdateUserBalance(user)
            for product in products_list:
                new_balance -= product.price
            self.connection.begin()
            transaction_complete = self.__insertPurchasesList(products_list, user)
            if transaction_complete:
                self.calculateAndUpdateUserBalance(user)
                self.connection.commit()
                return True
            else:
                self.connection.rollback()
                logger.error("Failed to insert checkout.")
                return False

    def __insertPurchasesList(self, products_list, user):
        success = True
        for product in products_list:
            success &= self.__insertPurchase(product, user)
        return success

    def __insertPurchase(self, product, user):
        insertPurchase = (
            "INSERT INTO purchases (product_id, user_id, price_then, price_factor_then) VALUES (%s, %s, %s, %s)"
        )
        try:
            logger.debug(self.dictCursor.mogrify(insertPurchase, ( product.id, user.id, product.price, user.price_factor) ))
            self.dictCursor.execute(insertPurchase, ( product.id, user.id, product.price, user.price_factor) )
            return True
        except Exception as err:
            self.connection.rollback()
            logger.error("Failed to insert purchase into database:")
            logger.error(err)
            return False
