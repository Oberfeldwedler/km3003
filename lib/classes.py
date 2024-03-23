import datetime

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


class ShoppingCart:
    def __init__(self, mySqlCaller, general_settings_dict):
        timeout = int(general_settings_dict['screen_timeout'])
        self.timeout = datetime.timedelta(seconds=timeout)
        self.mySqlCaller = mySqlCaller
        self.products_list = []
        self.user = []

    def resetTimestamp(self):
        self.timestamp = datetime.datetime.now()

    def reset(self):
        self.products_list = []
        self.user = []

    def checkout(self):
        for product in self.productList:
            self.insertPurchaseIntoDatabase(self, product.id, self.user.id, self.price_then)
        self.reset()
