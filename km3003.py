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
inactivity_timeout = int(general_settings_dict['screen_timeout_ms'])
message_timeout = int(general_settings_dict['message_timeout_ms'])

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
    [ sg.Push(), sg.Text("Geht grod ned!", font=("Arial", 44), text_color= "purple", key="-MESSAGE-"), sg.Push() ],
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
last_database_connection_state = "Up"

shopping_cart = classes.ShoppingCart(database_caller)
scanner = scanner.Scanner(serial_settings_dict)

def refreshTimer(timeout, timer_id, custom_key):
    window.timer_stop(timer_id)
    return window.timer_start(timeout, key=custom_key, repeating=False)

def refreshInactivityTimer():
    global inactivity_timer_id
    inactivity_timer_id = refreshTimer(inactivity_timeout, inactivity_timer_id, "-INACTIVITY_TIMER-")

def refreshMessageTimer():
    global message_timer_id
    message_timer_id = refreshTimer(message_timeout, message_timer_id, "-MESSAGE_TIMER-")

def stopMessageTimer():
    window.timer_stop(message_timer_id)
     

def reset():
    for product in shopping_cart.products_list:
        window[('-ROW-', product.sequential_product_row_number)].update(visible=False)
    window['-MEMBER-'].update('Bitte Ausweis scannen')
    window['-SUM-'].update('0€')
    shopping_cart.reset()

def layout_switcher(event, values):
    switched = False
    if  event == '-DATABASE_CONNECTION_INTERRUPTED-':
            window['-MESSAGE_LAYOUT-'].update(visible=False)
            window['-CHECKOUT_LAYOUT-'].update(visible=True)
            window['-MESSAGE-'].update('Datenbank nicht erreichbar!')
            stopMessageTimer()
            switched = True
    elif event == '-CHECKOUT_SUCCESSFULL-':
            window['-MESSAGE_LAYOUT-'].update(visible=True)
            window['-CHECKOUT_LAYOUT-'].update(visible=False)
            window['-MESSAGE-'].update(f"Erfolg! Guthaben: {values['-CHECKOUT_SUCCESSFULL-']}")
            refreshMessageTimer()
            switched = True
    elif event == '-CHECKOUT_FAILED-':
            window['-MESSAGE_LAYOUT-'].update(visible=True)
            window['-CHECKOUT_LAYOUT-'].update(visible=False)
            window['-MESSAGE-'].update(f"Das hat nicht geklappt.")
            refreshMessageTimer()
            switched = True
    # return to default by db reconnect
    elif event == '-DATABASE_CONNECTION_RESTORED-':
            window['-MESSAGE_LAYOUT-'].update(visible=False)
            window['-CHECKOUT_LAYOUT-'].update(visible=True)
            switched = True
    # return to default by timer
    elif event == '-MESSAGE_TIMER-':
            window['-MESSAGE_LAYOUT-'].update(visible=False)
            window['-CHECKOUT_LAYOUT-'].update(visible=True)
            switched = True
    return switched
 
while True:
    event, values = window.read(timeout=1000)
    if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
        break

    if( event != "-RESET-" and
        event != "-INACTIVITY_TIMER-" and 
        event != "__TIMEOUT__" ):
            refreshInactivityTimer()

    if layout_switcher(event, values):
        continue
    
    if last_database_connection_state == "Down" and database_caller.is_connected():
        window.write_event_value('-DATABASE_CONNECTION_RESTORED-', True)
        continue

    if last_database_connection_state == "Up" and not database_caller.is_connected():
        database_caller.reEstablishConnection()
        window.write_event_value('-DATABASE_CONNECTION_INTERRUPTED-', True)
        continue

    if event == "-CHECKOUT-":
        if shopping_cart.checkout():
            shopping_cart.refreshUser()
            window.write_event_value('-CHECKOUT_SUCCESSFULL-', shopping_cart.user.current_balance)
        else:
            window.write_event_value('-CHECKOUT_FAILED-', shopping_cart.user.current_balance)
        reset()
        continue

    if( event == "-INACTIVITY_TIMER-" or
        event == "-RESET-" ):
            reset()
            continue
    
    if event[0] == '-DEL-':
        row_number = event[1]
        shopping_cart.removeProductByRowNumber(row_number)
        window[('-ROW-',row_number)].update(visible=False)
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

        refreshInactivityTimer()


scanner.close()
database_caller.closeConnection()
window.close()
