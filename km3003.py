import datetime
import configparser
import PySimpleGUI as sg

from lib import mysql
from lib import classes
from lib import scanner

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
    sg.Button( 'Zurücksetzen', size=20 ), sg.Button('Buchen', expand_x=True ) 
]]
layout = [
    [ sg.Frame( 'Fachschaftsmitglied', header , expand_x=True, element_justification='center' ) ],
    [ sg.Frame( 'Einkaufsliste', productList , expand_x=True, expand_y=True ) ],
    [ sg.Frame( '', footer, expand_x=True ) ]
]


config = configparser.ConfigParser()
config.read('km3003.conf')
general_settings_dict = dict(config['general'])
mysql_settings_dict = dict(config['mysql'])
serial_settings_dict = dict(config['serial'])

database_caller = mysql.MySql(mysql_settings_dict)
database_caller.establishConnection()
database_caller.createDictCursor()


km3003 = classes.ShoppingCart(database_caller, general_settings_dict)
scanner = scanner.Scanner(serial_settings_dict)



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


# Event Loop to process "events" and get the "values" of the inputs
while True:
    # now = datetime.datetime.now()
    # print(scanner.getBarcode(self))

    #     result, type = database_caller.runBarcodeAgainstDatabase(item)
    #     if result == "user":
    #         mainShoppingCart.user = result
    #     elif result == "product":
    #         mainShoppingCart.products_list.append(result)
    #     else:
    #         print("Barcode not unique in database or unknown.")
    #     mainShoppingCart.resetTimestamp()

    
    event, values = window.read(timeout=50)
    if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
        break

    # if event == "Reset":
    #     mainShoppingCart.reset()

    # if event == "Checkout":
    #     mainShoppingCart.checkout()

    # # if event == "activity????":
    # #     mainShoppingCart.resetTimestamp()


    # if (now-mainShoppingCart.timestamp).total_seconds >= 10:
    #     mainShoppingCart.reset()


# close mysql stuff
# close serial stuff
window.close()
