from nicegui import ui, app
import configparser

# --- Load Settings (Keep your existing config logic) ---
config = configparser.ConfigParser()
config.read('km3003.conf')
theme_color = 'purple' # Example mapping from your config

# --- State Management ---
# NiceGUI handles state changes automatically. 
# We don't need window.write_event_value calls.
class State:
    cart = []
    total_sum = 0.0
    member_text = 'Bitte Ausweis scannen'

state = State()

def update_sum():
    state.total_sum = sum(p.price for p in state.cart)
    # Refresh the UI parts that need it
    sum_label.set_text(f'{state.total_sum:.2f}€')
    cart_container.refresh()

def add_product(product):
    state.cart.append(product)
    update_sum()

def reset_cart():
    state.cart = []
    state.member_text = 'Bitte Ausweis scannen'
    member_label.set_text(state.member_text)
    update_sum()

# --- UI Layout ---
# Using Tailwind CSS classes for styling (the strings like 'w-full', 'p-4')
with ui.column().classes('w-full h-screen items-stretch'):
    
    # Header / Member Area
    with ui.card().classes('w-full p-4 items-center bg-gray-100'):
        ui.label('Fachschaftsmitglied').classes('text-xl font-bold')
        member_label = ui.label(state.member_text).classes('text-2xl text-purple-600')

    # Body / Cart (Scrollable)
    with ui.scroll_area().classes('flex-grow p-4 border'):
        @ui.refreshable
        def render_cart():
            for i, product in enumerate(state.cart):
                with ui.row().classes('w-full justify-between items-center border-b p-2'):
                    ui.label(product.brand)
                    ui.label(product.name)
                    ui.label(f'{product.price}€')
                    # Delete button
                    ui.button('X', on_click=lambda idx=i: remove_item(idx)).classes('bg-red-500 text-white')
        
        cart_container = render_cart()

    # Footer / Sum & Actions
    with ui.row().classes('w-full p-4 bg-gray-200 justify-between items-center'):
        ui.label('Summe').classes('text-2xl')
        sum_label = ui.label('0.00€').classes('text-4xl font-bold')

    with ui.row().classes('w-full p-4 gap-4 h-24'):
        ui.button('Zurücksetzen', on_click=reset_cart).classes('h-full text-xl w-1/4 bg-gray-500')
        ui.button('Buchen', on_click=lambda: ui.notify('Checkout logic here')).classes(f'h-full text-xl flex-grow bg-{theme_color}-600')

def remove_item(index):
    if 0 <= index < len(state.cart):
        state.cart.pop(index)
        update_sum()

# --- Run in Native Mode (Kiosk) ---
# This uses pywebview under the hood to create the window
ui.run(
    title='KM3003',
    fullscreen=True, # Reads from your config
    native=True,     # <--- This triggers pywebview
    reload=False     # Disable reload for production
)