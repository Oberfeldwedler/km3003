import mysql.connector
from lib import classes

class MySqlDataError(Exception):
    """Raised when data fetched from database is inconsistent."""

class MySql:
    def __init__(self, mySqlSettingsDict):
        self.hostAddress = mySqlSettingsDict["hostaddress"]
        self.portNumber = int(mySqlSettingsDict["portnumber"])
        self.username = mySqlSettingsDict["username"]
        self.password = mySqlSettingsDict["password"]
        self.database = mySqlSettingsDict["database"]

    def establishConnection(self):
        try:
            self.cnx = mysql.connector.connect(user=self.username, password=self.password,
                                    host=self.hostAddress, port=self.portNumber,
                                    database=self.database)
        except mysql.connector.Error as err:
            print(err)

    def createDictCursor(self):
        self.dictCursor = self.cnx.cursor(buffered = True, dictionary = True)
        
    def closeConnection(self):
        self.cnx.close()
       
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

    def insertPurchaseIntoDatabase(self, product_id, user_id, price_then):
        insertPurchase = (
            "INSERT INTO purchases (product_id, user_id, price_then) VALUES (%s, %s, %s)"
        )
        print(insertPurchase)
        try:
            self.dictCursor.execute(insertPurchase, ( product_id, user_id, price_then ) )
            self.cnx.commit()
        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))

        #  +Calc and update current_balance in user table

        # do everything in 1 transaction
            

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