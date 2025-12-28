import re
import configparser
import logging.handlers
from nicegui import ui, app

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

database_caller = mysql.MySql(mysql_settings_dict)


# ====================================================================
# Shopping cart
# ====================================================================

shopping_cart = classes.ShoppingCart(database_caller)

def calculateTotalCheckoutSum(products_list):
    sum = 0
    for product in products_list:
        sum += product.price
    return sum


# ====================================================================
# Scanner
# ====================================================================
def scannerStateChangeCallback(newScannerState):
    pass

if str2bool(serial_settings_dict["console_input"]):
    scanner = scanner.ConsoleScanner(serial_settings_dict)
    logger.warning("Console reader enabled! Barcode reader will not work!")
    logger.warning("  Set  [serial]/console_input to False to reenable the barcode reader!")
else:
    scanner = scanner.SerialScanner(serial_settings_dict, scannerStateChangeCallback)

def processBarcode(barcode):
    if barcode:
        logger.info(f"New barcode was scanned: {barcode}")
        result = database_caller.runBarcodeAgainstDatabase(barcode)

        if isinstance(result, classes.User):
            shopping_cart.user = result
            current_balance = database_caller.calculateAndUpdateUserBalance(result)
            if result.price_factor != 1.0:
                pass
                # window['-MEMBER-'].update(f"{result.first_name} {result.last_name} {result.emoji}  PF: {result.price_factor}  Guthaben: {current_balance}€")
            else:
                pass
                # window['-MEMBER-'].update(f"{result.first_name} {result.last_name} {result.emoji}  Guthaben: {current_balance}€")
            logger.debug(f"User '{result.first_name} {result.last_name} {result.emoji}' was detected!")
        elif isinstance(result, classes.Product):
            shopping_cart.products_list.append(result)
            # window.extend_layout(window['-PRODUCT_LIST-'], [ result.generateRow() ])
            total_checkout_sum = calculateTotalCheckoutSum(shopping_cart.products_list)
            # window['-SUM-'].update(f"{total_checkout_sum}€")
            logger.debug(f"Product '{result.brand} {result.name}' was detected!")
        else:
            # window.write_event_value('-BARCODE_UNKNOWN-', item)
            pass

def scanner_poller():
    barcode = scanner.getBarcode()
    if barcode:
        processBarcode(barcode)

ui.timer(0.1, scanner_poller)


# ====================================================================
# Buttons
# ====================================================================

def reset():
    for product in shopping_cart.products_list:
        # delete all items here
        pass
    shopping_cart.reset()

def checkout():
    # if event == "-CHECKOUT-":
    #     if shopping_cart.checkout():
    #         user_balance = database_caller.getUserBalance(shopping_cart.user)
    #         window.write_event_value('-CHECKOUT_EVENT-', user_balance)
    #     else:
    #         window.write_event_value('-CHECKOUT_EVENT-', None)
    #     reset()
    #     continue
    pass

# ====================================================================
# Lifecycle events
# ====================================================================

def onShutdown():
    scanner.close()
    database_caller.closeConnection()
app.on_shutdown(onShutdown)



# ====================================================================
# GUI
# ====================================================================


# Set primary color
ui.colors(primary=general_settings_dict['primary_color'])

# Define styles for scroll bar
custom_thumb_style = {'width': '25px', 'border-radius': '12px', 'backgroundColor': '#9c27b0', 'opacity': 0.5}
custom_bar_style = {'width': '25px', 'backgroundColor': '#f1f1f1', 'opacity': 0.2}

# Remove global padding
ui.query('.nicegui-content').classes('p-0')

with ui.column().classes('w-full h-screen p-4 gap-4 no-wrap'):

    # Header
    with ui.card().classes('w-full shadow-md'):
        ui.label("Fachschaftsmitglied").classes('text-bold text-2xl text-primary')
        ui.label("Bitte Ausweis scannen").classes('text-grey-7 pt-0')

    # Shopping cart
    with ui.card().classes('w-full grow overflow-hidden no-wrap shadow-lg'):
        ui.label("Warenkorb").classes('text-bold text-xl mb-2')

        with ui.scroll_area() \
            .classes('w-full grow') \
            .props(f':thumb-style="{custom_thumb_style}" :bar-style="{custom_bar_style}" visible'):
            with ui.column().classes('w-full gap-2 p-1 pr-10'): # pr-4 schafft Platz für den breiten Scrollbar
                for i in range(15): 
                    with ui.row().classes('w-full items-center bg-slate-50 px-4 py-3 rounded-lg border border-slate-100'):
                        ui.label(f'Getränk {i+1}').classes('grow font-medium')
                        ui.label(f'{i+1},50 €').classes('px-4 font-bold')
                        ui.button(icon='delete').props('flat round').classes('text-gray-400 hover:text-red-500')
        
        ui.separator().classes('my-2')
        
        with ui.row().classes('w-full items-center px-2 py-2'):
            ui.label("Gesamt:").classes('text-xl font-medium')
            ui.space()
            ui.label("24,50 €").classes('text-4xl font-black text-primary')

    # Buttons
    with ui.row().classes('w-full gap-4 items-end'):
        ui.button("ZURÜCKSETZEN", color='red', icon='refresh') \
            .classes('flex-[1] h-20 text-base font-bold rounded-xl opacity-80')
        ui.button("JETZT BUCHEN", color='primary', icon='check_circle') \
            .classes('flex-[4] h-20 text-2xl font-bold rounded-xl shadow-lg')

ui.run(uvicorn_reload_excludes='.*, .py[cod], .sw.*, ~*, *.log, logs/*, logs/km3003.log')