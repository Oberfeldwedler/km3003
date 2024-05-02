import mysql.connector
from lib import classes

class MySqlDataError(Exception):
    """Raised when data fetched from database is inconsistent."""

class MySql:
    def __init__(self, mySqlSettingsDict):
        self.hostAddress = mySqlSettingsDict["host_address"]
        self.portNumber = int(mySqlSettingsDict["port_number"])
        self.username = mySqlSettingsDict["username"]
        self.password = mySqlSettingsDict["password"]
        self.database = mySqlSettingsDict["database"]
        self.cnx = mysql.connector.connect()

    def closeConnection(self):
        try:
            self.cnx.close()
        except:
            return

    def establishConnection(self):
        try:
            self.cnx = mysql.connector.connect(user=self.username, password=self.password,
                                    host=self.hostAddress, port=self.portNumber,
                                    database=self.database, 
                                    connect_timeout=1)
            print("Connection to database established.")
            self.dictCursor = self.cnx.cursor(dictionary=True, buffered=True)
        except mysql.connector.Error as err:
            print(err)


    def reEstablishConnection(self):
        self.closeConnection()
        self.establishConnection()

    def isConnected(self):
        if self.cnx:
            return self.cnx.is_connected()
       
    def getUserFromDatabase(self, barcode):
        getUsers = ("SELECT * FROM users WHERE barcode=%s")
        try:
            self.dictCursor.execute(getUsers, ( barcode, ) )
            rowCount = self.dictCursor.rowcount
            if rowCount == 1:
                dataDict = self.dictCursor.fetchone()
                return classes.User(dataDict['id'], barcode, dataDict['name'], dataDict['current_balance'])
            if rowCount > 1:
                raise MySqlDataError
            else:
                return None
        except MySqlDataError:
            print("Barcode is not unique in user database.")
            return None

    def getProductFromDatabase(self, barcode):
        getProducts = ("SELECT * FROM products WHERE barcode=%s")
        try:
            self.dictCursor.execute(getProducts, ( barcode, ) )
            rowCount = self.dictCursor.rowcount
            if rowCount == 1:
                dataDict = self.dictCursor.fetchone()
                return classes.Product(dataDict['id'], barcode, dataDict['name'], dataDict['sell_price'])
            if rowCount > 1:
                raise MySqlDataError
            else:
                return None
        except MySqlDataError:
            print("Barcode is not unique in product database.")
            return None

    def runBarcodeAgainstDatabase(self, barcode):
        user = self.getUserFromDatabase(barcode)
        product = self.getProductFromDatabase(barcode)
        
        if product != None and user == None:
            return product
        elif product == None and user != None:
            return user
        elif product != None and user != None:
            print("Barcode is not unique in database.")
            return None
        else:
            return None

    def commitCurrentTransaction(self):
        try:
            self.cnx.commit()
            return True
        except mysql.connector.Error as err:
            print("Failed to commit transaction: {}".format(err))
            return False

    def updateUserBalance(self, user_id, new_balance):
        updateBalance = ( 
            "UPDATE users SET current_balance=%s WHERE (id=%s)"
        )
        try:
            self.dictCursor.execute(updateBalance, ( new_balance, user_id ) )
            return True
        except mysql.connector.Error as err:
            print("Failed to create database transaction: {}".format(err))
            return False

    def insertPurchasesList(self, products_list, user_id):
        success = True
        for product in products_list:
            success &= self.insertPurchase(product.id, user_id, product.price)
        return success   

    def insertPurchase(self, product_id, user_id, price_then):
        insertPurchase = (
            "INSERT INTO purchases (product_id, user_id, price_then) VALUES (%s, %s, %s)"
        )
        try:
            self.dictCursor.execute(insertPurchase, ( product_id, user_id, price_then ) )
            return True
        except mysql.connector.Error as err:
            print("Failed to create database transaction: {}".format(err))
            return False
