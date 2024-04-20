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

    def is_connected(self):
        if self.cnx:
            return self.cnx.is_connected()

    def createDictCursor(self):
        self.dictCursor = self.cnx.cursor(buffered = True, dictionary = True)
        
       
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
        try:
            if product != None and user == None:
                return product, "product"
            elif product == None and user != None:
                return user, "user"
            elif product != None and user != None:
                raise MySqlDataError
            else:
                return None, None
        except MySqlDataError:
            print("Barcode is not unique in database.")
            return None, None
        
    def insertPurchasesListIntoDatabase(self, products_list, user_id):
        success = True
        for product in products_list:
            success &= self.insertPurchaseIntoDatabase(product.id, user_id, product.price)
            
        if not success:
            return False

        try:
            self.cnx.commit()
            return True
        except mysql.connector.Error as err:
            print("Failed to commit transaction: {}".format(err))
            return False
        

    def insertPurchaseIntoDatabase(self, product_id, user_id, price_then):
        insertPurchase = (
            "INSERT INTO purchases (product_id, user_id, price_then) VALUES (%s, %s, %s)"
        )
        try:
            self.dictCursor.execute(insertPurchase, ( product_id, user_id, price_then ) )
            return True
        except mysql.connector.Error as err:
            print("Failed to create database transaction: {}".format(err))
            return False


    def checkout(self, user_id, products_list):
        for product in products_list:
            self.insertPurchaseIntoDatabase(user_id, product)


# test_user = database_caller.getUserFromDatabase("301260000015887")
# print(test_user.name)
# test_product =database_caller.getProductFromDatabase("20290443")
# print(test_product.name)
# result, type = database_caller.runBarcodeAgainstDatabase("301260000015887")
# print(result)

# database_caller.insertPurchaseIntoDatabase(2, 3, 0.4)