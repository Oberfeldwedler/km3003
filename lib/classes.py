import PySimpleGUI as sg


class User:
    def __init__(self, id, barcode, name, current_balance):
        self.id = id
        self.barcode = barcode
        self.name = name
        self.current_balance = current_balance


class Product:
    def __init__(self, id, barcode, name, price):
        self.id = id
        self.barcode = barcode
        self.name = name
        self.price = price

    def generateRow(self, item_num):
        product_row = [ 
            sg.pin(
                sg.Col( [[
                    sg.Text(self.name), 
                    sg.Push(),
                    sg.Text(self.price), 
                    sg.Button('X', size=5, k=('-DEL-', item_num)),
                ]], 
                k=('-ROW-', item_num),
                expand_x=True),
            expand_x=True
            )
        ]
        return product_row


class ShoppingCart:
    def __init__(self, database_caller, general_settings_dict, window):
        self.database_caller = database_caller
        self.timeout = 1000*int(general_settings_dict['screen_timeout'])
        self.window = window
        self.window.metadata = 0
        self.disabled = False
        self.products_list = []
        self.user = []
        self.refresh_timer_id = self.startResetTimer()

    def startResetTimer(self):
        refresh_timer_id = self.window.timer_start(self.timeout, key='-RESET_CHECKOUT_TIMER-', repeating=False)
        return refresh_timer_id

    def refreshResetTimer(self):
        self.window.timer_stop(self.refresh_timer_id)
        self.refresh_timer_id = self.startResetTimer()

    def reset(self):
        print("Reset")
        self.products_list = []
        self.user = []
        self.window['-PRODUCT_LIST-'].layout([[]])
        # self.window.metadata = 0
        self.refreshResetTimer()

    def checkout(self):
        for product in self.productList:
            self.database_caller.insertPurchaseIntoDatabase(self, product.id, self.user.id, self.price_then)
        self.reset()
