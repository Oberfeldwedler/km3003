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
timeout = int(general_settings_dict['screen_timeout_ms'])

sg.theme(general_settings_dict['theme'])

sum_row = [[ 
    sg.Column( [[sg.Text('Summe')]] ), 
    sg.Push(), 
    sg.Column( [[sg.Text('0€', key='-SUM-')]] )
]]

product_list = [
    [ sg.Col( [], expand_x=True, key='-PRODUCT_LIST-') ]
]

member_row = [[ sg.Text('Bitte Ausweis scannen', key='-MEMBER-') ]]

body = [
    [ product_list ],
    [ sg.VPush() ], 
    [ sg.HorizontalSeparator() ],
    [ sum_row ]
]

footer = [
    [ sg.Button( 'Zurücksetzen', size=20, key='-RESET-'), sg.Button('Buchen', expand_x=True , key='-CHECKOUT-') ]
]

message_layout = [
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
        sg.Column(message_layout, key='-MESSAGE_LAYOUT-', expand_x=True, expand_y=True)
    ]
]




# Create the Window
# TODO: window global?
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
# window.print_event_values=True

inactivity_timer_id = 0
message_timer_id = 0

database_caller = mysql.MySql(mysql_settings_dict)

shopping_cart = classes.ShoppingCart(database_caller, general_settings_dict, window)
scanner = scanner.Scanner(serial_settings_dict)

def refreshTimer(timer_id):
    window.timer_stop(timer_id)
    return window.timer_start(timeout, key='-INACTIVITY_TIMER-', repeating=False)

def reset():
    for product in shopping_cart.products_list:
        window[('-ROW-', product.sequential_product_row_number)].update(visible=False)
    window['-MEMBER-'].update('Bitte Ausweis scannen')
    window['-SUM-'].update('0€')
    shopping_cart.reset()

def layout_switcher(event):
    if  event == '-DATABASE_CONNECTION_INTERRUPTED-':
        if database_caller.is_connected():  
            window['-MESSAGE_LAYOUT-'].update(visible=False)
            window['-CHECKOUT_LAYOUT-'].update(visible=True)
        else:  
            window['-CHECKOUT_LAYOUT-'].update(visible=False)
            window['-MESSAGE_LAYOUT-'].update(visible=True)
        return True
    return False
 
while True:
    event, values = window.read(timeout=1000)
    if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
        break

    if not event == "__TIMEOUT__":
        print("__LOOP__")
        print(event)
        # print(values)

    if( event != "-RESET-" and
        event != "-INACTIVITY_TIMER-" and 
        event != "__TIMEOUT__" ):
            inactivity_timer_id = refreshTimer(inactivity_timer_id)

    if layout_switcher(event):
        continue

    if not database_caller.is_connected():
        database_caller.reEstablishConnection()
        window.write_event_value('-DATABASE_CONNECTION_INTERRUPTED-', True)
        continue

    item=scanner.getBarcode()
    if item:
        item = item.strip()
        result, type = database_caller.runBarcodeAgainstDatabase(item)
        if type == "user":
            shopping_cart.user = result
            window['-MEMBER-'].update(result.name)
        elif type == "product":
            shopping_cart.products_list.append(result)
            window.extend_layout(window['-PRODUCT_LIST-'], [ result.generateRow() ])
            sum = 0
            for product in shopping_cart.products_list:
                sum += product.price
            window['-SUM-'].update(f"{sum}€")
        else:
            print("Barcode not unique in database or unknown.")

        inactivity_timer_id = refreshTimer(inactivity_timer_id)

    if event[0] == '-DEL-':
        row_number = event[1]
        shopping_cart.removeProductByRowNumber(row_number)
        window[('-ROW-',row_number)].update(visible=False)

    if( event == "-INACTIVITY_TIMER-" or
        event == "RESET" ):
            reset()
            continue

    if event == "-CHECKOUT-":
        shopping_cart.checkout()
        reset()
    

scanner.close()
database_caller.closeConnection()
window.close()
