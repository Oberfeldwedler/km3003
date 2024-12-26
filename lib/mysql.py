import pymysql.cursors

from lib import classes

import logging

logger = logging.getLogger(__name__)

class MySqlDataError(Exception):
    """Raised when data fetched from database is inconsistent."""

class MySql:
    def __init__(self, mySqlSettingsDict):
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
        logger.info("Connection to database closed.")
        try:
            self.connection.close()
        except:
            logging.warning("Connection to database could not be closed! Ignoring!")
            pass
       
    def ensureDatabaseConnection(self):
        lastConnectionState = self.__connectionState
        if self.connection == None:
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

    def getUserFromDatabase(self, barcode):
        query = ("SELECT * FROM users WHERE barcode=%s")
        try:

            logger.debug(self.dictCursor.mogrify(query, ( barcode, ) ))
            self.dictCursor.execute(query, ( barcode, ) )
            rowCount = self.dictCursor.rowcount
            
            if rowCount == 1:
                dataDict = self.dictCursor.fetchone()
                return classes.User(barcode, dataDict['first_name'], dataDict['last_name'], dataDict['emoji'])
            elif rowCount > 1:
                logger.error(f"Barcode {barcode} does not identify a unique user! ({rowCount} results)")
            self.connection.commit()
        except MySqlDataError as err:
            self.connection.rollback()
            logger.error("Error during SELECT from table USER:")
            logger.error(err)
        return None
        
    def getProductFromDatabase(self, barcode):
        query = ("SELECT * FROM products WHERE barcode=%s")
        try:

            logger.debug(self.dictCursor.mogrify(query, ( barcode, ) ))
            self.dictCursor.execute(query, ( barcode, ) )
            rowCount = self.dictCursor.rowcount
            
            if rowCount == 1:
                dataDict = self.dictCursor.fetchone()
                return classes.Product(barcode, dataDict['name'], dataDict['sell_price'], dataDict['brand'])
            elif rowCount > 1:
                logger.error(f"Barcode {barcode} does not identify a unique product! ({rowCount} results)")
            self.connection.commit()
        except MySqlDataError as err:
            logger.error("Error during SELECT from table USER")
            logger.error(err)
            
        return None

    def runBarcodeAgainstDatabase(self, barcode):
        user = self.getUserFromDatabase(barcode)
        product = self.getProductFromDatabase(barcode)
        
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

    def getUserBalance(self, user):
        get_user_balance = ("SELECT current_balance FROM users WHERE barcode=%s")
        try:
            self.dictCursor.execute(get_user_balance, ( user.barcode, ) ) 
            dataDict = self.dictCursor.fetchone()
            self.connection.commit()
            return dataDict['current_balance']
        except Exception as err:
            self.connection.rollback()
            logger.error("Failed to get user balance:")
            logger.error(err)
            return None  
 
    def calculateUserBalance(self, user):
        get_purchases = ("SELECT price_then FROM purchases WHERE user_barcode=%s")
        get_deposits = ("SELECT amount FROM deposits WHERE user_barcode=%s")
        
        sum_of_purchases = 0
        sum_of_deposits = 0
        
        try:

            logger.debug(self.dictCursor.mogrify(get_purchases, ( user.barcode, )))
            self.dictCursor.execute(get_purchases, ( user.barcode, ) ) 

            for purchase in self.dictCursor:
                sum_of_purchases += purchase["price_then"]
                
            logger.debug(self.dictCursor.mogrify(get_deposits, ( user.barcode, )))
            self.dictCursor.execute(get_deposits, ( user.barcode, ) )

            for deposit in self.dictCursor:
                sum_of_deposits += deposit["amount"]
            self.connection.commit()
                
        except Exception as err:
            self.connection.rollback()
            logger.error("Failed to calculate current user balance:")
            logger.error(err)
            return None
        
        new_balance = sum_of_deposits-sum_of_purchases
        return new_balance

    def updateUserBalance(self, user, new_balance):
        updateBalance = ( 
            "UPDATE users SET current_balance=%s WHERE (barcode=%s)"
        )
        logger.debug(self.dictCursor.mogrify(updateBalance, ( new_balance, user.barcode ) ))
        try:
            self.connection.begin()
            self.dictCursor.execute(updateBalance, ( new_balance, user.barcode ) )
            self.connection.commit()
            return True
        except Exception as err:
            self.connection.rollback()
            logger.error("Failed to update user balance in database:")
            logger.error(err)
            return False

    def insertCheckout(self, products_list, user):
        new_balance = self.calculateAndUpdateUserBalance(user)
        for product in products_list:
            new_balance -= product.price
        self.connection.begin()
        transaction_complete = self.insertPurchasesList(products_list, user)
        transaction_complete &= self.updateUserBalance(user, new_balance)
        if transaction_complete:
            user = self.calculateAndUpdateUserBalance(user)
            self.connection.commit()
            return True
        else:
            self.connection.rollback()
            logger.error("Failed to insert checkout.")
            return False

    def calculateAndUpdateUserBalance(self, user):
        new_balance = self.calculateUserBalance(user)
        self.updateUserBalance(user, new_balance)
        return new_balance

    def insertPurchasesList(self, products_list, user):
        success = True
        for product in products_list:
            success &= self.insertPurchase(product, user)
        return success

    def insertPurchase(self, product, user):
        insertPurchase = (
            "INSERT INTO purchases (product_barcode, user_barcode, price_then) VALUES (%s, %s, %s)"
        )
        try:
            logger.debug(self.dictCursor.mogrify(insertPurchase, ( product.barcode, user.barcode, product.price ) ))
            self.dictCursor.execute(insertPurchase, ( product.barcode, user.barcode, product.price ) )
            return True
        except Exception as err:
            self.connection.rollback()
            logger.error("Failed to insert purchase into database:")
            logger.error(err)
            return False
