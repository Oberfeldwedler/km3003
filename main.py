import PySimpleGUI as sg
import mysql.connector
from mysql.connector import errorcode
import configparser


sg.theme('BluePurple')
font = ("Arial", 15)
initialWidth=951
initialHeight=540

header = [[ 
    sg.Text('Bitte Ausweis scannen') 
]]
product0 = [[
    sg.Column( [[ sg.Text('Getränk') ]] ), 
    sg.Push(),
    sg.Column( [[ sg.Text('15€') ]] ), 
    sg.Column( [[ sg.Button('X', size=5) ]] )
]] 
sum = [[ 
    sg.Column( [[sg.Text('Summe')]] ), 
    sg.Push(), 
    sg.Column( [[sg.Text('80€')]] )
]]
productList = [
    [ product0 ],
    [ sg.VPush() ], 
    [ sg.HorizontalSeparator() ],
    [ sum ]
]
footer = [[ 
    # sg.Button('Reset'), sg.Push() ,sg.Button('Buchen')
    sg.Button( 'Reset', size=20 ), sg.Button('Buchen', expand_x=True ) 
]]
layout = [
    [ sg.Frame( 'Fachschaftsmitglied', header , expand_x=True, element_justification='center' ) ],
    [ sg.Frame( 'Einkaufsliste', productList , expand_x=True, expand_y=True ) ],
    [ sg.Frame( '', footer, expand_x=True ) ]
]


class User:
    def __init__(self, id, barcode, name, current_balance):
        self.id = id
        self.barcode = barcode
        self.name = name
        self.current_balance = current_balance


class Product:
    def __init__(self, id, barcode, name, price):
        self.id = id
        self.barcode = barcode
        self.name = name
        self.price = price
   

class MySqlDataError(Exception):
    """Raised when data fetched from database is inconsistent."""

class MySqlCaller:  
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
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
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
                return User(dataDict['id'], barcode, dataDict['name'], dataDict['current_balance'])
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
                return Product(dataDict['id'], barcode, dataDict['name'], dataDict['sell_price'])
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

    def checkout(self, user_id, products_list):
        for product in products_list:
            self.insertPurchaseIntoDatabase(user_id, product)


class ShoppingCart:
    products_list = None
    user = None

    def __init__(self, mySqlCaller):
        self.mySqlCaller = mySqlCaller



config = configparser.ConfigParser()
config.read('km3003.conf')
mysql_settings_dict = dict(config['mysql'])

database_caller = MySqlCaller(mysql_settings_dict)
database_caller.establishConnection()
database_caller.createDictCursor()

mainShoppingCart = ShoppingCart(database_caller)

test_user = database_caller.getUserFromDatabase("301260000015887")
print(test_user.name)
test_product =database_caller.getProductFromDatabase("20290443")
print(test_product.name)
# result, type = database_caller.runBarcodeAgainstDatabase("301260000015887")
# print(result)

database_caller.insertPurchaseIntoDatabase(2, 3, 0.4)



# # Create the Window
# window = sg.Window (
#     'Window Title', 
#     layout, 
#     no_titlebar=False,  
#     size=(initialWidth,initialHeight), 
#     location=(0,0), 
#     keep_on_top=True,
#     font=font
# )
# window.Resizable=True



# Event Loop to process "events" and get the "values" of the inputs
# while True:
#     event, values = window.read()
    


#     if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
#         break
#     print('You entered ', values[0])

# window.close()
