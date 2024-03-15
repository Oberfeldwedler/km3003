import PySimpleGUI as sg
import mysql.connector
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

class mySqlCaller_Exception(Exception):
    """Raised when an error occurred during the communication with MySQL Server"""

class mySqlCaller:  
    def __init__(self, mySqlSettingsDict):
        self.hostAddress = mySqlSettingsDict["hostAddress"]
        self.portNumber = int(mySqlSettingsDict["portNumber"])
        self.username = mySqlSettingsDict["username"]
        self.password = mySqlSettingsDict["password"]
        self.database = mySqlSettingsDict["database"]

    def establishConnectionToServer(self):
        try:
            cnx = mysql.connector.connect(user=self.username, password=self.password,
                                    host=self.hostAddress, port=self.portNumber,
                                    database=self.database)
        except mysql.connector.Error as err:
            raise mySqlCaller_Exception(
                f"ERROR: Could not establish a Database connection to {self.hostAddress}:{self.portNumber}")
        
    # def closeConnectionToServer(self):
    #     cnx.cursor()


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



# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()



    if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
        break
    print('You entered ', values[0])

window.close()
