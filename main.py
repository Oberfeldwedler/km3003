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


class user:
    def __init__(self, barcode, mySqlCaller):
        self.barcode = barcode
        self.name, self.current_balance =  mySqlCaller.getUserFromBarcode()


class product:
    def __init__(self, barcode, mySqlCaller):
        self.barcode = barcode
        self.name, self.price = mySqlCaller.getProductFromBarcode()
   


class mySqlCaller_Exception(Exception):
    """Raised when an error occurred during the communication with MySQL Server"""

class mySqlCaller:  
    def __init__(self, mySqlSettingsDict):
        self.hostAddress = mySqlSettingsDict["hostAddress"]
        self.portNumber = int(mySqlSettingsDict["portNumber"])
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
        self.dictCursor = cnx.cursor()
        
    def closeConnection(self):
        self.cnx.close()
       
    def getUserInfoFromBarcode(self, barcode):
        getUser = ("SELECT * FROM employees WHERE barcode=%s")
        try:
            self.dictCursor.execute(getUser, barcode)
            if self.dictCursor.rowcount > 1: 
                raise mySqlCaller_Exception
        # except mysql.connector.Error as err:
        #     print("Syntax error: {}".format(err))
        except mySqlCaller_Exception:
            print ("User barcode is not unique in Database.")
            return None
        return dictCursor.fetchone()




# Create the Window
window = sg.Window (
    'Window Title', 
    layout, 
    no_titlebar=False,  
    size=(initialWidth,initialHeight), 
    location=(0,0), 
    keep_on_top=True,
    font=font
)
window.Resizable=True



config = configparser.ConfigParser()
config.read('km3003.conf')
mySqlSettingsDict = dict(config['mysql'])

mySqlCaller = mySqlCaller(mySqlSettingsDict)
mySqlCaller.establishConnection()
mySqlCaller.createDictCursor()


# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()



    if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
        break
    print('You entered ', values[0])

window.close()
