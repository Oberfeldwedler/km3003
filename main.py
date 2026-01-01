import os
import re
import logging
import asyncio
import configparser
import logging.handlers
from nicegui import ui, app

from lib import mysql
from lib import classes
from lib import scanner


config = configparser.ConfigParser()
config.read('km3003.conf')
general_settings_dict = dict(config['general'])
mysql_settings_dict = dict(config['mysql'])
serial_settings_dict = dict(config['serial'])
inactivity_timeout = int(general_settings_dict.get('screen_timeout_ms', '30000'))
message_timeout = int(general_settings_dict.get('message_timeout_ms', '2000'))

def str2bool(value : str) -> bool:
    return value.lower() in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'ja', 'jawoll', 'definitiv']


# ====================================================================
# Logging
# ====================================================================

LOG_DIR = general_settings_dict.get('log_dir', './logs')
LOG_FILE = os.path.join(LOG_DIR, "km3003.log")
EVENT_LOG = os.path.join(LOG_DIR, "events.csv") # Separate file for events with human interaction

if not os.path.exists(f"{LOG_DIR}"):
    os.mkdir(f"{LOG_DIR}")
    
formatter = logging.Formatter(
    "[%(levelname)-7s] [%(asctime)s] %(name)10s: %(message)s", 
    datefmt="%Y-%m-%d %H:%M:%S"
)

file_handler = logging.handlers.RotatingFileHandler(
    f"{LOG_FILE}", 
    maxBytes=(1048576*5), 
    backupCount=7, 
    encoding='utf-8', 
    delay=True
)
file_handler.setFormatter(formatter)

# Event Handler - Only for events with human interaction
event_handler = logging.handlers.RotatingFileHandler(
    EVENT_LOG, maxBytes=1048576, backupCount=10, delay=True
)
event_handler.setFormatter(logging.Formatter("%(asctime)s,%(message)s"))

root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

# Clear existing handlers to prevent duplicate console output in NiceGUI
root_logger.handlers.clear()

# Add the file handler to root so it captures everything (App + Libraries)
file_handler.setLevel(general_settings_dict.get("logging", "INFO").upper())
root_logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(general_settings_dict.get("logging", "INFO").upper())
root_logger.addHandler(console_handler)

# Create a specialized logger for events with human interaction
logger_event = logging.getLogger("event")
logger_event.propagate = False 
logger_event.addHandler(event_handler)
logger_event.setLevel(logging.INFO)

logger = logging.getLogger(__name__)


# ====================================================================
# System health
# ====================================================================

# Globaler Speicher für den Systemstatus
system_status = {"db": "up", "scanner": "up", "error_message": ""}

async def backgroundHealthCheck():
    """Läuft als eigenständiger Hintergrund-Task."""
    while True:
        try:
            checkSystemHealth()
        except Exception as e:
            logger.error(f"Fehler im Health-Check: {e}")
        
        # Wait 2 seconds for the next check
        await asyncio.sleep(2)

def checkSystemHealth():
    """Diese Funktion läuft unabhängig von der UI."""
    logger.debug('Checking system health!')
    global system_status
        
    database_state, _ = database_caller.ensureDatabaseConnection()
    scanner_state = scanner_instance.getConnectionState()

    system_status["db"] = database_state
    system_status["scanner"] = scanner_state

    errors = []
    if database_state != "up": errors.append("Datenbank down")
    if scanner_state != "up": errors.append("Scanner down")
    system_status["error_message"] = " & ".join(errors)



# ====================================================================
# Lifecycle events and other init tasks
# ====================================================================

database_caller = None
shopping_cart = None
scanner_instance = None

def onStartup():
    global database_caller, shopping_cart, scanner_instance

    if os.path.exists(LOG_FILE):
        try:
            # This only works if no other process (like the reloader) has the file open
            file_handler.doRollover()
            logger.info("=========== NEW START OF KM3003 ===========")
        except PermissionError:
            # On Windows, if the Manager process is still holding a lock, 
            # we simply skip the rollover for this specific process.
            pass

    if str2bool(serial_settings_dict.get('console_input', 'False')):
        scanner_instance = scanner.ConsoleScanner(serial_settings_dict)
        logger.warning("Console reader enabled! Barcode reader will not work!")
        logger.warning("  Set  [serial]/console_input to False to reenable the barcode reader!")
    else:
        scanner_instance = scanner.SerialScanner(serial_settings_dict, scannerStateChangeCallback)

    database_caller = mysql.MySql(mysql_settings_dict)
    database_caller.establishConnection()
    shopping_cart = classes.ShoppingCart(database_caller, update_ui_display)

    asyncio.create_task(backgroundHealthCheck())

    ui.timer(0.1, scanner_poller)
app.on_startup(onStartup)

def onShutdown():
    scanner_instance.close()
    database_caller.closeConnection()
app.on_shutdown(onShutdown)


# ====================================================================
# Scanner
# ====================================================================
def scannerStateChangeCallback(newScannerState):
    pass

def processBarcode(barcode):
    if barcode:
        result = database_caller.runBarcodeAgainstDatabase(barcode)
        if isinstance(result, classes.User):
            shopping_cart.addUser = result

            if hasattr(main_page.member_container, 'empty_message') and main_page.member_container.empty_message:
                main_page.member_container.empty_message.delete()
                main_page.member_container.empty_message = None

            main_page.member_container.clear()

            with main_page.member_container:
                result.generateRow()

            logger.info(f"User '{result.first_name} {result.last_name} {result.emoji}' was detected!")
            logger_event.info(f"User '{result.first_name} {result.last_name} {result.emoji}' was detected!")
        elif isinstance(result, classes.Product):
            shopping_cart.addProduct(result)

            if main_page.cart_container.empty_message:
                main_page.cart_container.empty_message.delete()
                main_page.cart_container.empty_message = None

            with main_page.cart_container:
                result.generateRow(shopping_cart.handleCartRemoval)

            logger.info(f"Product '{result.brand} {result.name}' was detected!")
            logger_event.info(f"Product '{result.brand} {result.name}' was detected!")
        else:
            logger.info(f"Unknown barcode {barcode} was scanned!")
            logger_event.info(f"Unknown barcode {barcode} was scanned!")
            ui.notify('Unbekannter Barcode', type='negative', classes='text-2xl q-pa-lg font-bold')
            pass

def scanner_poller():
    barcode = scanner_instance.getBarcode()
    if barcode:
        logger.info(f"New barcode was scanned: {barcode}")
        processBarcode(barcode)


# ====================================================================
# Buttons
# ====================================================================

def reset():
    shopping_cart.reset()

def checkout():
    # if shopping_cart.checkout():
    #     user_balance = database_caller.getUserBalance(shopping_cart.getUser())
    #     window.write_event_value('-CHECKOUT_EVENT-', user_balance)
    # else:
    #     window.write_event_value('-CHECKOUT_EVENT-', None)
    # reset()
    pass


# ====================================================================
# GUI
# ====================================================================

@ui.page('/')
def main_page():

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
            ui.label("Fachschaftsmitglied").classes('text-bold text-xl mb-2')
            main_page.member_container = ui.card().classes('w-full no-shadow')
            with main_page.member_container:
                main_page.member_container.empty_message = ui.label("Bitte Ausweis scannen").classes('text-grey-7 pt-0')

        # Shopping cart
        with ui.card().classes('w-full grow overflow-hidden no-wrap shadow-lg'):
            ui.label("Warenkorb").classes('text-bold text-xl mb-2')

            with ui.scroll_area() \
                .classes('w-full grow') \
                .props(f':thumb-style="{custom_thumb_style}" :bar-style="{custom_bar_style}" visible'):

                main_page.cart_container = ui.column().classes('w-full gap-2 p-1 pr-10') # pr-4 schafft Platz für den breiten Scrollbar
                with main_page.cart_container:
                    main_page.cart_container.empty_message = ui.label("Dein Warenkorb ist leer.").classes('text-grey-7 pt-0')

            ui.separator().classes('my-2')
            
            with ui.row().classes('w-full items-center px-2 py-2'):
                ui.label("Gesamt:").classes('text-xl font-medium')
                ui.space()
                main_page.total_checkout_sum = ui.label("0 €").classes('text-4xl font-black text-primary')

        # Buttons
        with ui.row().classes('w-full gap-4 items-end'):
            ui.button("ZURÜCKSETZEN", color='red', icon='refresh') \
                .classes('flex-[1] h-20 text-base font-bold rounded-xl opacity-80')
            ui.button("JETZT BUCHEN", color='primary', icon='check_circle') \
                .classes('flex-[4] h-20 text-2xl font-bold rounded-xl shadow-lg')
        
        # Simulator for scanner input (hidden by default)
        if str2bool(serial_settings_dict.get('console_input', 'False')): 
            with ui.row().classes('items-center'):
                ui.label('Simulate Barcode:')
                # When user presses Enter, it processes the barcode
                sim_input = ui.input(on_change=lambda e: None) \
                    .on('keydown.enter', lambda: [processBarcode(sim_input.value), sim_input.set_value('')])
            
            # Focus the input automatically so you can just type and press enter
            sim_input.run_method('focus')

        def refresh_overlay():
                # Reagiert auf die Ergebnisse des Timers aus onStartup
                if system_status["error_message"]:
                    main_page.error_message.set_text(system_status["error_message"])
                    main_page.error_overlay.visible = True
                else:
                    main_page.error_overlay.visible = False

        # Dieser Timer läuft im Browser und schaltet nur das Overlay um
        ui.timer(1.0, refresh_overlay)

        # Error overlay (hidden by default)
        with ui.column().classes('absolute-full items-center justify-center z-50') \
                .style('background-color: rgba(0, 0, 0, 0.8); backdrop-filter: blur(4px)') \
                as main_page.error_overlay:
            main_page.error_overlay.visible = False # Initial ausblenden
            
            ui.icon('warning', color='white').classes('text-9xl mb-4')
            main_page.error_message = ui.label('').classes('text-white text-4xl font-bold text-center px-10')
            ui.spinner(size='lg', color='white').classes('mt-8')

def update_ui_display():
    """
    Refreshes all dynamic UI elements based on the current shopping_cart state.
    """
    # Manage the "Empty Cart" message
    if shopping_cart.empty():
        # If the container is empty and message isn't there, add it
        if not hasattr(main_page, 'empty_message') or main_page.cart_container.empty_message is None:
            with main_page.cart_container:
                main_page.cart_container.empty_message = ui.label("Dein Warenkorb ist leer.").classes('text-grey-7 pt-0')
    else:
        # If there are items, delete the empty message if it exists
        if hasattr(main_page, 'empty_message') and main_page.cart_container.empty_message:
            main_page.cart_container.empty_message.delete()
            main_page.cart_container.empty_message = None

    total = shopping_cart.calculateTotalCheckoutSum()
    total_text = f"{total:.2f} €"
    user = shopping_cart.getUser()
    if user:
        logger.debug(f"{user.price_factor}")
    # if user and user.price_factor != 1.0:
        discounted = total * user.price_factor
        total_text = f"{total:.2f}€ × {user.price_factor} = {discounted:.2f}€"
        
    main_page.total_checkout_sum.set_text(total_text)

# Protected Entry Point
if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title='KM3004',
        reload=True,
        # Prevent the reloader from watching the log files to avoid restart loops
        uvicorn_reload_excludes=f'{LOG_DIR}/*, *.log'
    )
