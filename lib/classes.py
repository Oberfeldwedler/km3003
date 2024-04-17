import PySimpleGUI as sg

class User:
    def __init__(self, id, barcode, name, current_balance):
        self.id = id
        self.barcode = barcode
        self.name = name
        self.current_balance = current_balance


class Product:

    sequential_product_row_counter = 0

    def __init__(self, id, barcode, name, price):
        self.id = id
        self.barcode = barcode
        self.name = name
        self.price = price
        self.sequential_product_row_number = Product.sequential_product_row_counter
        Product.sequential_product_row_counter += 1

    def generateRow(self):
        product_row = [ 
            sg.pin(
                sg.Col( [[
                    sg.Text(self.name), 
                    sg.Push(),
                    sg.Text(self.price), 
                    sg.Button('X', size=5, k=('-DEL-', self.sequential_product_row_number)),
                ]], 
                k=('-ROW-', self.sequential_product_row_number),
                expand_x=True),
            expand_x=True
            )
        ]
        return product_row


class ShoppingCart:
    def __init__(self, database_caller, general_settings_dict, window):
        self.database_caller = database_caller
        self.timeout = int(general_settings_dict['screen_timeout_ms'])
        self.window = window
        # self.window.metadata = 0
        self.disabled = False
        self.products_list = []
        self.user = None
        self.refresh_timer_id = self.startInactivityTimer()

    def startInactivityTimer(self):
        refresh_timer_id = self.window.timer_start(self.timeout, key='-INACTIVITY_TIMER-', repeating=False)
        return refresh_timer_id

    def stopInactivityTimer(self):
        self.window.timer_stop(self.refresh_timer_id)

    def refreshInactivityTimer(self):
        self.stopInactivityTimer()
        self.refresh_timer_id = self.startInactivityTimer()

    def reset(self):
        self.user = None
        self.products_list = []
        self.stopInactivityTimer()

    def checkout(self):
        checkout_ready = not (self.user == None) and self.products_list
        if checkout_ready:
            if self.database_caller.insertPurchasesListIntoDatabase(self.products_list, self.user.id):
                self.window.write_event_value('-CHECKOUT_SUCESSFUL-', True)
                self.window.write_event_value('-MESSAGE-', "Checkout sucessfull")
        else:
            self.window.write_event_value('-CHECKOUT_SUCESSFUL-', False)    
            self.window.write_event_value('-MESSAGE-', "Checkout failed")

    def removeProductByRowNumber(self, row_number):
        for product in self.products_list:
            if product.sequential_product_row_number == row_number:
                self.products_list.remove(product)
