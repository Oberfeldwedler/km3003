import configparser
import PySimpleGUI as sg

from lib import mysql
from lib import classes
# from lib import scanner

sg.theme('BluePurple')
font = ("Arial", 15)
initialWidth=951
initialHeight=540

product_row = [[
    sg.Column( [[ sg.Text('Getränk') ]] ), 
    sg.Push(),
    sg.Column( [[ sg.Text('15€') ]] ), 
    sg.Column( [[ sg.Button('X', size=5, key=('-DEL-', 0)) ]]) 
]] 

sum_row = [[ 
    sg.Column( [[sg.Text('Summe')]] ), 
    sg.Push(), 
    sg.Column( [[sg.Text('80€')]] )
]]

product_list = [
    [ sg.Col( [], expand_x=True, key='-PRODUCT_LIST-') ]
]

member_row = [[ sg.Text('Bitte Ausweis scannen') ]]

body = [
    [ product_list ],
    [ sg.VPush() ], 
    [ sg.HorizontalSeparator() ],
    [ sum_row ]
]
 
footer = [
    [ sg.Button( 'Zurücksetzen', size=20, key='-RESET-'), sg.Button('Buchen', expand_x=True , key='-CHECKOUT-') ]
]

layout = [
    [ sg.Frame( 'Fachschaftsmitglied', member_row , expand_x=True, element_justification='center' ) ],
    [ sg.Frame( 'Einkaufsliste', body , expand_x=True, expand_y=True ) ],
    [ sg.Frame( '', footer, expand_x=True ) ]
]


config = configparser.ConfigParser()
config.read('km3003.conf')
general_settings_dict = dict(config['general'])
mysql_settings_dict = dict(config['mysql'])
serial_settings_dict = dict(config['serial'])

database_caller = mysql.MySql(mysql_settings_dict)
# database_caller.establishConnection()
# database_caller.createDictCursor()

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

shopping_cart = classes.ShoppingCart(database_caller, general_settings_dict, window)
# scanner = scanner.Scanner(serial_settings_dict)

# Event Loop to process "events" and get the "values" of the inputs
while True:

    if not database_caller.is_connected():
        database_caller.reEstablishConnection()
        # window.popup("Database Connection Lost")
        print("No connection to database.")
        shopping_cart.reset()
        continue

    # item=scanner.getBarcode()
    # if item:
    #     item = item.strip()
    #     result, type = database_caller.runBarcodeAgainstDatabase(item)
    #     if type == "user":
    #         shopping_cart.user = result
    #     elif type == "product":
    #         shopping_cart.products_list.append(result)
    #         window.metadata += 1
    #         window.extend_layout(window['-PRODUCT_LIST-'], [ result.generateRow(window.metadata) ] )
    #     else:
    #         print("Barcode not unique in database or unknown.")

        shopping_cart.refreshResetTimer()

        for product in shopping_cart.products_list:
            print(product.name)


    event, values = window.read(timeout=1000)
    if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
        break

    # if event:
    #     print(event[0]) 
    #     print(event[1]) 

    if event[0] == '-DEL-':
        window[('-ROW-', event[1])].update(visible=False)

    if event == "-RESET-":
        shopping_cart.reset()

    if event == "-CHECKOUT-":
        shopping_cart.checkout()

    if event == "-RESET_CHECKOUT_TIMER-":
        shopping_cart.reset()

    if event:
        shopping_cart.refreshResetTimer()




# close mysql stuff
# close serial stuff
window.close()
