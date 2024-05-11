import mysql.connector
import pymysql.cursors

from lib import classes

import logging

logger = logging.getLogger(__name__)

class MySqlDataError(Exception):
    """Raised when data fetched from database is inconsistent."""

class MySql:
    def __init__(self, mySqlSettingsDict):
        self.__connectionActive = False
        self.hostAddress = mySqlSettingsDict["host_address"]
        self.portNumber = int(mySqlSettingsDict["port_number"])
        self.username = mySqlSettingsDict["username"]
        self.password = mySqlSettingsDict["password"]
        self.database = mySqlSettingsDict["database"]
        self.connection = None  

    def establishConnection(self):
        try:
            logger.debug("Trying to connect to database:")
            logger.debug(f"HOST={self.hostAddress}:{self.portNumber}, USER={self.username}, DB={self.database}")
            self.connection = pymysql.connect(user=self.username, password=self.password,
                                    host=self.hostAddress, port=self.portNumber,
                                    database=self.database, 
                                    read_timeout=1, write_timeout=1, connect_timeout=1)
            self.dictCursor = self.connection.cursor(pymysql.cursors.DictCursor)
            self.__connectionActive = True
            logger.info("Connection to database established.")
            return True
        except Exception as err:
            logger.error("Cannot connect to database!")
            logger.error(err)
            self.__connectionActive = False
            return False
       
    def ensureDatabaseConnection(self):
        lastConnectionState = self.__connectionActive
        if self.connection == None:
            self.establishConnection()
        else:
            try:
                self.connection.ping(reconnect=True)
                self.__connectionActive = True
            except:
                self.__connectionActive = False

        connectionStateChanged = self.__connectionActive ^ lastConnectionState #XOR

        return self.__connectionActive, connectionStateChanged

       
    def getUserFromDatabase(self, barcode):
        query = ("SELECT * FROM users WHERE barcode=%s")
        try:
            
            logger.debug(f"QUERY(SELECT, USER): bardcode={barcode}")
            self.dictCursor.execute(query, ( barcode, ) )
            rowCount = self.dictCursor.rowcount
            
            if rowCount == 1:
                dataDict = self.dictCursor.fetchone()
                return classes.User(dataDict['id'], barcode, dataDict['name'], dataDict['current_balance'])
            elif rowCount > 1:
                logger.error(f"Barcode {barcode} does not identify a unique user! ({rowCount} results)")
        
        except MySqlDataError as err:
            logger.error("Error during SELECT from table USER")
            logger.error(err)
            
        return None
        
    def getProductFromDatabase(self, barcode):
        
        query = ("SELECT * FROM products WHERE barcode=%s")
        try:
            
            logger.debug(f"QUERY(SELECT, PRODUCT): bardcode={barcode}")
            self.dictCursor.execute(query, ( barcode, ) )
            rowCount = self.dictCursor.rowcount
            
            if rowCount == 1:
                dataDict = self.dictCursor.fetchone()
                return classes.Product(dataDict['id'], barcode, dataDict['name'], dataDict['sell_price'])
            elif rowCount > 1:
                logger.error(f"Barcode {barcode} does not identify a unique product! ({rowCount} results)")
                
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

    def beginTransaction(self):
        self.connection.begin()

    def commitCurrentTransaction(self):
        try:
            self.connection.commit()
            logger.debug("Commiting query to database.")
            return True
        except mysql.connector.Error as err:
            logger.error("Failed to commit transaction to database!")
            logger.error(err)
            return False

    def calculateUserBalance(self, user):
        
        get_purchases = ("SELECT price_then FROM purchases WHERE user_id=%s")
        get_deposits = ("SELECT amount FROM deposits WHERE user_id=%s")
        
        sum_of_purchases = 0
        sum_of_deposits = 0
        
        try:
            
            logger.debug(f"QUERY(SELECT, PURCHASES): user_id={user.id}")
            self.dictCursor.execute(get_purchases, ( user.id, ) ) 
            for purchase in self.dictCursor:
                sum_of_purchases += purchase["price_then"]
                
            logger.debug(f"QUERY(SELECT, DEPOSITS): user_id={user.id}")
            self.dictCursor.execute(get_deposits, ( user.id, ) )
            for deposit in self.dictCursor:
                sum_of_deposits += deposit["amount"]
                
        except MySqlDataError as err:
            logger.error("Failed to calculate current user balance.")
            logger.error(err)
            return None
        
        new_balance = sum_of_deposits-sum_of_purchases
        return new_balance

    def updateUserBalance(self, user, new_balance):
        updateBalance = ( 
            "UPDATE users SET current_balance=%s WHERE (id=%s)"
        )
        try:
            logger.debug(f"QUERY(UPDATE, USERS): user={user.id}, current_balance={new_balance}")
            self.dictCursor.execute(updateBalance, ( new_balance, user.id ) )
            return True
        
        except mysql.connector.Error as err:
            logger.error("Failed to update user balance in database:")
            logger.error(err)
            return False

    def calculateAndUpdateUserBalance(self, user):
        new_balance = self.calculateUserBalance(user)
        self.updateUserBalance(user, new_balance)
        user.current_balance = new_balance
        return user

    def insertPurchasesList(self, products_list, user):
        success = True
        for product in products_list:
            success &= self.insertPurchase(product, user)
        return success

    def insertPurchase(self, product, user):
        insertPurchase = (
            "INSERT INTO purchases (product_id, user_id, price_then) VALUES (%s, %s, %s)"
        )
        try:
            logger.debug(f"QUERY(INSERT, PURCHASES): product_id={product.id}, user_id={user.id}")
            self.dictCursor.execute(insertPurchase, ( product.id, user.id, product.price ) )
            return True
        except mysql.connector.Error as err:
            logger.error("Failed to insert purchase into database:")
            logger.error(err)
            return False
