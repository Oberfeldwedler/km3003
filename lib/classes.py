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

    def row(self):
        product_row = [[
            sg.Column( [[ sg.Text(self.name) ]] ), 
            sg.Push(),
            sg.Column( [[ sg.Text(self.sell_price) ]] ), 
            sg.Column( [[ sg.Button('X', size=5, k=('DEL_self', self.id) ) ]] ),
        ]] 

        return product_row


class ShoppingCart:
    def __init__(self, mySqlCaller, general_settings_dict, window):
        self.mySqlCaller = mySqlCaller
        self.timeout = 1000*int(general_settings_dict['screen_timeout'])
        self.window = window
        self.products_list = []
        self.user = []
        self.refresh_timer_id = self.startResetTimer()

    def startResetTimer(self):
        refresh_timer_id = self.window.timer_start(self.timeout, key='RESET_CHECKOUT_TIMER', repeating=False)
        return refresh_timer_id

    def refreshResetTimer(self):
        self.window.timer_stop(self.refresh_timer_id)
        self.refresh_timer_id = self.startResetTimer()

    def reset(self):
        self.products_list = []
        self.user = []
        self.window.timer_stop(self.refresh_timer_id)

    def checkout(self):
        for product in self.productList:
            self.insertPurchaseIntoDatabase(self, product.id, self.user.id, self.price_then)
        self.reset()
