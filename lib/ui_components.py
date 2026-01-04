from nicegui import ui
from lib import classes

def render_user_header(user, balance):
    """
    Renders the user header area with name and current balance.
    """
    name = f"{user.emoji} {user.first_name} {user.last_name} {user.emoji}"
    
    if user.price_factor != 1.0:
        sub_text = f'Guthaben: {balance:.2f}€ \t\t PF: {user.price_factor}'
    else:
        sub_text = f'Guthaben: {balance:.2f}€'

    with ui.column().classes('w-full items-center'):
        label = ui.label(name).classes('text-3xl font-bold text-primary text-center')
        ui.label(sub_text).classes('text-lg text-grey-7 text-center')
    
    return label

def render_cart_item(product, on_delete_callback, price_factor):
    """
    Renders a single row in the shopping cart.
    """
    price = product.price * price_factor
    price_text = f'{price:.2f} €'

    with ui.row().classes('w-full items-center bg-slate-50 px-4 py-3 rounded-lg border border-slate-100') as row:
        ui.label(f'{product.brand} {product.name}').classes('grow font-medium')
        ui.label(price_text).classes('px-4 font-bold')
        
        # Note: on_delete_callback(product) is called to update the Logical Shopping Cart
        # row.delete() is called to remove the Visual Element immediately
        ui.button(icon='delete', on_click=lambda: [row.delete(), on_delete_callback(product)]) \
            .props('flat round') \
            .classes('text-gray-400 hover:text-red-500')
    return row

def render_action_buttons(on_reset_click, on_checkout_click):
    with ui.row().classes('w-full gap-4 items-end'):
        ui.button("ZURÜCKSETZEN", color='red', icon='refresh', on_click=on_reset_click) \
            .classes('flex-[1] h-20 text-base font-bold rounded-xl opacity-80')
        ui.button("JETZT BUCHEN", color='primary', icon='check_circle', on_click=on_checkout_click) \
            .classes('flex-[4] h-20 text-2xl font-bold rounded-xl shadow-lg')