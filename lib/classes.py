import logging
from nicegui import ui, app

logger = logging.getLogger(__name__)
logger_event = logging.getLogger("event")

class User:
    def __init__(self, id, first_name, last_name, emoji, price_factor):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.emoji = emoji
        self.price_factor = float(price_factor)


class Product:
    sequential_product_row_counter = 0

    def __init__(self, id, name, price, brand):
        self.id = id
        self.name = name
        self.price = float(price)
        self.brand = brand
        self.sequential_product_row_number = Product.sequential_product_row_counter
        Product.sequential_product_row_counter += 1


class ShoppingCart:
    def __init__(self, database_caller, uiUpdateCallback):
        self.__database_caller = database_caller
        self.__products_list = []
        self.__user = None
        self.uiUpdateCallback = uiUpdateCallback

    def getUser(self):
        return self.__user
    
    def addUser(self, user):
        self.__user=user
        self.uiUpdateCallback()

    def empty(self):
        return not self.__products_list

    def getProducts(self):
        return self.__products_list

    def addProduct(self, product):
        self.__products_list.append(product)
        self.uiUpdateCallback()

    def handleCartRemoval(self, product):
        """This callback function is called directly by the product and handles the 'Data' side of deletion"""
        if product in self.__products_list:
            self.__products_list.remove(product)
            logger.info(f"Removed {product.name} from cart.")
            self.uiUpdateCallback()

    def reset(self):
        self.__user = None
        self.__products_list = []
        logger.info(f"Removed user and products due to reset.")
        self.uiUpdateCallback()

    def checkout(self):
        if not self.__user or not self.__products_list:
            return False

        success = self.__database_caller.insertCheckout(self.__products_list, self.__user)
                
        if success:
            self.reset()

        return success
  
    def calculateTotalCheckoutSum(self):
        sum = 0.0
        for product in self.__products_list:
            sum += product.price
        return sum
