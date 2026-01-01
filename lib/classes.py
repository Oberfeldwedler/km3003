import logging
from nicegui import ui, app

logger = logging.getLogger(__name__)
logger_event = logging.getLogger("event")

class User:
    def __init__(self, id, first_name, last_name, emoji, price_factor, getCurrentBalanceCallback):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.emoji = emoji
        self.price_factor = price_factor
        self.getCurrentBalanceCallback = getCurrentBalanceCallback

    def generateRow(self):
        balance = self.getCurrentBalanceCallback(self)

        display_text = f"{self.first_name} {self.last_name} {self.emoji}"
        balance_text = f"Guthaben: {balance:.2f}€"

        with ui.column().classes('w-full items-center'):
            label = ui.label(display_text).classes('text-3xl font-bold text-primary text-center')
            ui.label(balance_text).classes('text-lg text-grey-7 text-center')
        
        return label
    

class Product:
    sequential_product_row_counter = 0

    def __init__(self, id, name, price, brand):
        self.id = id
        self.name = name
        self.price = price
        self.brand = brand
        self.sequential_product_row_number = Product.sequential_product_row_counter
        Product.sequential_product_row_counter += 1

    def generateRow(self, onDeleteCallback):
        with ui.row().classes('w-full items-center bg-slate-50 px-4 py-3 rounded-lg border border-slate-100') as row:
            ui.label(f'{self.brand} {self.name}').classes('grow font-medium')
            ui.label(f'{self.price:.2f} €').classes('px-4 font-bold')
            ui.button(icon='delete', on_click=lambda: [row.delete(), onDeleteCallback(self)]) \
                .props('flat round') \
                .classes('text-gray-400 hover:text-red-500')
        return row


class ShoppingCart:
    def __init__(self, database_caller, uiUpdateCallback):
        self.database_caller = database_caller
        self.__products_list = []
        self.__user = None
        self.uiUpdateCallback = uiUpdateCallback

    def reset(self):
        self.__user = None
        self.__products_list = []

    def checkout(self):
        checkout_ready = not (self.__user == None) and self.__products_list
        if checkout_ready:
            return self.database_caller.insertCheckout(self.__products_list, self.__user)
        else:
            return False

    def refreshUser(self):
        if self.__user:
            self.__user = self.database_caller.getUserFromDatabase(self.__user.barcode)
    
    def empty(self):
        return not self.__products_list

    def addProduct(self, product):
        self.__products_list.append(product)
        self.uiUpdateCallback()

    def addUser(self, user):
        self.__user=user
        self.uiUpdateCallback()

    def getUser(self):
        return self.__user

    def handleCartRemoval(self, product):
        """This function handles the 'Data' side of deletion"""
        if product in self.__products_list:
            self.__products_list.remove(product)
            logger.info(f"Removed {product.name} from cart.")
            logger_event.info(f"Removed {product.name} from cart.")
            self.uiUpdateCallback()

    def calculateTotalCheckoutSum(self):
        sum = 0
        for product in self.__products_list:
            sum += product.price
        return sum