import re
import configparser
import logging.handlers
import PySimpleGUI as sg

from lib import mysql
from lib import classes
from lib import scanner

import os
import logging

config = configparser.ConfigParser()
config.read('km3003.conf')
general_settings_dict = dict(config['general'])
mysql_settings_dict = dict(config['mysql'])
serial_settings_dict = dict(config['serial'])
inactivity_timeout = int(general_settings_dict['screen_timeout_ms'])
message_timeout = int(general_settings_dict['message_timeout_ms'])

def str2bool(value : str) -> bool:
    return value.lower() in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'ja', 'jawoll', 'definitiv']

if not os.path.exists("logs/"):
    os.mkdir("logs")
    
formatter = logging.Formatter("[%(levelname)-7s] [%(asctime)s] %(name)10s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
logging.basicConfig()
logging.getLogger().setLevel(general_settings_dict.get("logging", "INFO").upper())
log_handler = logging.handlers.RotatingFileHandler("logs/km3003.log", maxBytes=(1048576*5), backupCount=7, encoding='utf-8')
logging.getLogger().addHandler(log_handler)
for handler in logging.getLogger().handlers:
    handler.setFormatter(formatter)
log_handler.doRollover()


logger = logging.getLogger(__name__)
logger_event = logging.getLogger("event")
logger.info("=========== NEW START OF KM3003 ===========")

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

footer = [[ 
    sg.Button('Zurücksetzen', 
              size=(20,2), 
              font=(general_settings_dict["font"], int(general_settings_dict["font_size"]) * 2),
              key='-RESET-'), 
    sg.Button('Buchen', 
              expand_x=True, 
              expand_y=True, 
              font=(general_settings_dict["font"], int(general_settings_dict["font_size"]) * 2),
              key='-CHECKOUT-') ]
]

message_layout = [
    [ sg.VPush() ],
    [ sg.Push(), sg.Text("Geht grod ned!", font=(general_settings_dict["font"], int(general_settings_dict["font_size"]) * 3), text_color= "purple", key="-MESSAGE-"), sg.Push() ],
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
        sg.Column(message_layout, key='-MESSAGE_LAYOUT-', expand_x=True, expand_y=True, visible=True)
    ]
]

if  str2bool(general_settings_dict['debug']):
    general_settings_dict['resizable'] = "True"
    general_settings_dict['no_titlebar'] = "False"
    general_settings_dict['maximize'] = "False"

window = sg.Window (
    'KM3003',
    layout, 
    size=( 
        general_settings_dict['initial_width'], 
        general_settings_dict['initial_height']
    ), 
    location=(0,0), 
    keep_on_top=str2bool(general_settings_dict['keep_on_top']),
    resizable=str2bool(general_settings_dict['resizable']),
    font=( 
        general_settings_dict['font'], 
        general_settings_dict['font_size'] 
    ),
    no_titlebar = str2bool(general_settings_dict["no_titlebar"])
)

if str2bool(general_settings_dict["maximize"]):
    window.finalize()
    window.maximize()

inactivity_timer_id = 0
message_timer_id = 0

database_caller = mysql.MySql(mysql_settings_dict)

shopping_cart = classes.ShoppingCart(database_caller)

def scannerStateChangeCallback(newScannerState):
    window.write_event_value('-SCANNER_CONNECTION_EVENT-', newScannerState)

if str2bool(serial_settings_dict["console_input"]):
    scanner = scanner.ConsoleScanner(serial_settings_dict)
    logger.warning("Console reader enabled! Barcode reader will not work!")
    logger.warning("  Set  [serial]/console_input to False to reenable the barcode reader!")
else:
    scanner = scanner.SerialScanner(serial_settings_dict, scannerStateChangeCallback)

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

def calculateTotalCheckoutSum(products_list):
    sum = 0
    for product in products_list:
        sum += product.price
    return sum

def reset():
    for product in shopping_cart.products_list:
        window[('-ROW-', product.sequential_product_row_number)].update(visible=False)
    window['-MEMBER-'].update('Bitte Ausweis scannen')
    window['-SUM-'].update('0€')
    shopping_cart.reset()

def showCheckoutLayout():
    if database_caller.getConnectionState() != "up":
        window.write_event_value('-DATABASE_CONNECTION_EVENT-', "down")
        return
    if scanner.getConnectionState() != "up":
        window.write_event_value('-SCANNER_CONNECTION_EVENT-', "down")
        return
    window['-MESSAGE_LAYOUT-'].update(visible=False)
    window['-CHECKOUT_LAYOUT-'].update(visible=True)

def showMessageLayout(message):
    logger.info(f"Displaying message: '{message}'")
    
    window['-MESSAGE_LAYOUT-'].update(visible=True)
    window['-CHECKOUT_LAYOUT-'].update(visible=False)
    window['-MESSAGE-'].update(message)

def layout_switcher(event, values):

    if event != "__TIMEOUT__":
        logger_event.debug(f"{event}")

    switched = False

    match event:
        case '-DATABASE_CONNECTION_EVENT-':
            if values['-DATABASE_CONNECTION_EVENT-'] == "up":
                showCheckoutLayout()
                switched = True
            else:
                showMessageLayout('Datenbank nicht erreichbar!')
                stopMessageTimer()
                switched = True

        case'-SCANNER_CONNECTION_EVENT-':
            if values['-SCANNER_CONNECTION_EVENT-'] == "up":
                showCheckoutLayout()
                switched = True
            else:
                showMessageLayout('Scanner nicht verfügbar!')
                stopMessageTimer()
                switched = True

        case '-CHECKOUT_EVENT-':
            if values['-CHECKOUT_EVENT-'] == None:
                showMessageLayout(f"Das hat nicht geklappt.")
                refreshMessageTimer()
                switched = True
            else:
                showMessageLayout(f"Erfolg! Guthaben: {values['-CHECKOUT_EVENT-']}")
                refreshMessageTimer()
                switched = True

        case '-MESSAGE_TIMER-':
            showCheckoutLayout()
            switched = True

        case '-BARCODE_UNKNOWN-':
            showMessageLayout(f"Unbekannter Barcode:\n{values['-BARCODE_UNKNOWN-']}")
            refreshMessageTimer()
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

    database_state, database_state_change = database_caller.ensureDatabaseConnection()

    if database_state_change:
        logger.debug(f"database_state_change: {database_state_change}")
        logger.debug(f"database_active: {database_state}")
        window.write_event_value('-DATABASE_CONNECTION_EVENT-', database_state)
        continue
    
    if event == "-CHECKOUT-":
        if shopping_cart.checkout():
            user_balance = database_caller.getUserBalance(shopping_cart.user)
            window.write_event_value('-CHECKOUT_EVENT-', user_balance)
        else:
            window.write_event_value('-CHECKOUT_EVENT-', None)
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
        total_checkout_sum = calculateTotalCheckoutSum(shopping_cart.products_list)
        window['-SUM-'].update(f"{ total_checkout_sum}€")        
        continue

    item=scanner.getBarcode()
    if item:
        item = item.strip()
        logger.info(f"New barcode was scanned: {item}")
        result = database_caller.runBarcodeAgainstDatabase(item)
             
        if isinstance(result, classes.User):
            shopping_cart.user = result
            current_balance = database_caller.calculateAndUpdateUserBalance(result)
            window['-MEMBER-'].update(f"{result.first_name} {result.last_name} {result.emoji}       Guthaben: {current_balance}€")
            logger.debug(f"User '{result.first_name} {result.last_name} {result.emoji}' was detected!")
        elif isinstance(result, classes.Product):
            shopping_cart.products_list.append(result)
            window.extend_layout(window['-PRODUCT_LIST-'], [ result.generateRow() ])
            total_checkout_sum = calculateTotalCheckoutSum(shopping_cart.products_list)
            window['-SUM-'].update(f"{total_checkout_sum}€")
            logger.debug(f"Product '{result.brand} {result.name}' was detected!")
        else:
            window.write_event_value('-BARCODE_UNKNOWN-', item)

        refreshInactivityTimer()


scanner.close()
database_caller.closeConnection()
window.close()
