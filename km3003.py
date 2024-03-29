import configparser
import PySimpleGUI as sg

from lib import mysql
from lib import classes
from lib import scanner

config = configparser.ConfigParser()
config.read('km3003.conf')
general_settings_dict = dict(config['general'])
mysql_settings_dict = dict(config['mysql'])
serial_settings_dict = dict(config['serial'])

sg.theme(general_settings_dict['theme'])

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

maintenance_layout = [
    [ sg.VPush() ],
    [ sg.Push(), sg.Text("Geht grod ned!", font=("Arial", 44), text_color= "purple" ), sg.Push() ],
    [ sg.VPush() ]
]

checkout_layout = [
    [ sg.Frame( 'Fachschaftsmitglied', member_row , expand_x=True, element_justification='center', key= '-HEADER-') ],
    [ sg.Frame( 'Warenkorb', body, expand_x=True, expand_y=True, key= '-BODY-') ],
    [ sg.Frame( '', footer, expand_x=True, key= '-FOOTER-' ) ]
]

layout = [
    [ 
        sg.Column(checkout_layout, key='-CHECKOUT_LAYOUT-', expand_x=True, expand_y=True, visible=False), 
        sg.Column(maintenance_layout, key='-MAINTENANCE_LAYOUT-', expand_x=True, expand_y=True)
    ]
] 

# Create the Window
window = sg.Window (
    'KM3003',
    layout, 
    no_titlebar=False,  
    size=( 
        general_settings_dict['initial_width'], 
        general_settings_dict['initial_height']
    ), 
    location=(0,0), 
    keep_on_top=True,
    font=( 
        general_settings_dict['font'], 
        general_settings_dict['font_size'] 
    )
)
window.Resizable=True

database_caller = mysql.MySql(mysql_settings_dict)
database_caller.establishConnection()

shopping_cart = classes.ShoppingCart(database_caller, general_settings_dict, window)
scanner = scanner.Scanner(serial_settings_dict)

while True:

    event, values = window.read(timeout=1000)
    if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
        break
    
    if event == '-REPAINT-':
        if database_caller.is_connected():  
            window['-MAINTENANCE_LAYOUT-'].update(visible=False)
            window['-CHECKOUT_LAYOUT-'].update(visible=True)
            shopping_cart.disabled = False
        else:  
            window['-CHECKOUT_LAYOUT-'].update(visible=False)
            window['-MAINTENANCE_LAYOUT-'].update(visible=True)
            shopping_cart.disabled = True
        continue

    if not database_caller.is_connected():
        database_caller.reEstablishConnection()
        window.write_event_value('-REPAINT-', True)
        continue

    item=scanner.getBarcode()
    if item:
        item = item.strip()
        result, type = database_caller.runBarcodeAgainstDatabase(item)
        if type == "user":
            shopping_cart.user = result
        elif type == "product":
            shopping_cart.products_list.append(result)
            window.metadata += 1
            window.extend_layout(window['-PRODUCT_LIST-'], [ result.generateRow(window.metadata) ] )
        else:
            print("Barcode not unique in database or unknown.")

        shopping_cart.refreshResetTimer()

        for product in shopping_cart.products_list:
            print(product.name)

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
