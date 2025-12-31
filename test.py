import re
import configparser
import logging.handlers
from nicegui import ui, app

from lib import mysql
from lib import classes
from lib import scanner

import os
import logging

from nicegui import ui

LOG_DIR = '../km3003_logs'
LOG_FILE = os.path.join(LOG_DIR, "km3003.log")
EVENT_LOG = os.path.join(LOG_DIR, "events.csv") # Separate file for events with human interaction

config = configparser.ConfigParser()
config.read('km3003.conf')
general_settings_dict = dict(config['general'])
mysql_settings_dict = dict(config['mysql'])
serial_settings_dict = dict(config['serial'])
inactivity_timeout = int(general_settings_dict['screen_timeout_ms'])
message_timeout = int(general_settings_dict['message_timeout_ms'])

def str2bool(value : str) -> bool:
    return value.lower() in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'ja', 'jawoll', 'definitiv']

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

# (Optional) Event Handler - Only for events with human interaction
event_handler = logging.handlers.RotatingFileHandler(
    EVENT_LOG, maxBytes=1048576, backupCount=10, delay=True
)
event_handler.setFormatter(logging.Formatter("%(asctime)s,%(message)s"))

root_logger = logging.getLogger()
root_logger.setLevel(general_settings_dict.get("logging", "INFO").upper())

# Clear existing handlers to prevent duplicate console output in NiceGUI
root_logger.handlers.clear()

# Add the file handler to root so it captures everything (App + Libraries)
root_logger.addHandler(file_handler)

# (Optional) Create a specialized logger for events with human interaction
logger_event = logging.getLogger("event")
logger_event.propagate = False 
logger_event.addHandler(event_handler)

logger = logging.getLogger(__name__)

# ====================================================================
# Lifecycle events
# ====================================================================

def onStartup():
    if os.path.exists(LOG_FILE):
        try:
            # This only works if no other process (like the reloader) has the file open
            logger.doRollover()
            logger.info("=========== NEW START OF KM3003 ===========")
        except PermissionError:
            # On Windows, if the Manager process is still holding a lock, 
            # we simply skip the rollover for this specific process.
            pass

app.on_startup(onStartup)

# ====================================================================
# GUI
# ====================================================================

@ui.page('/')
def main_page():
    ui.label('Hello NiceGUI!')

# Protected Entry Point
if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        reload=True,
        # Prevent the reloader from watching the log files to avoid restart loops
        uvicorn_reload_excludes=f'{LOG_DIR}/*, *.log'
    )

