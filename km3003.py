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
shopping_cart = classes.ShoppingCart(database_caller)


def scannerStateChangeCallback(newScannerState):
    pass

def barcodeScannedCallback(barcode):
    # This runs in the background thread!
    # We "hand off" the update_ui function to the main thread:
    app.add_main_queue_callback(barcode)

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

if str2bool(serial_settings_dict["console_input"]):
    scanner = scanner.ConsoleScanner(serial_settings_dict, barcodeScannedCallback)
    logger.warning("Console reader enabled! Barcode reader will not work!")
    logger.warning("  Set  [serial]/console_input to False to reenable the barcode reader!")
else:
    scanner = scanner.SerialScanner(serial_settings_dict, scannerStateChangeCallback, barcodeScannedCallback)






def calculateTotalCheckoutSum(products_list):
    sum = 0
    for product in products_list:
        sum += product.price
    return sum

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




scanner.close()
database_caller.closeConnection()
window.close()
