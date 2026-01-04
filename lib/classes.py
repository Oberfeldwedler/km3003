import logging
from decimal import Decimal
from nicegui import ui, app

logger = logging.getLogger(__name__)
logger_event = logging.getLogger("event")

class User:
    def __init__(self, id, first_name, last_name, emoji, price_factor):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.emoji = emoji
        # If the input price is a float, converting it directly to Decimal can preserve the floating point imprecision 
        # (e.g., Decimal(1.1) # becomes 1.1000000000000000888...).
        # Converting to string first (Decimal("1.1")) ensures it creates the exact number you expect.
        self.price_factor = Decimal(str(price_factor))


class Product:
    sequential_product_row_counter = 0

    def __init__(self, id, name, price, brand):
        self.id = id
        self.name = name
        # If the input price is a float, converting it directly to Decimal can preserve the floating point imprecision 
        # (e.g., Decimal(1.1) # becomes 1.1000000000000000888...).
        # Converting to string first (Decimal("1.1")) ensures it creates the exact number you expect.
        self.price = Decimal(str(price))
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
        total_sum = Decimal('0.00')
        for product in self.__products_list:
            total_sum += product.price
        return total_sum
