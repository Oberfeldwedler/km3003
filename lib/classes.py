import PySimpleGUI as sg

class User:
    def __init__(self, barcode, name, surname, emoji):
        self.barcode = barcode
        self.name = name
        self.surname = surname
        self.emoji = emoji

class Product:
    sequential_product_row_counter = 0

    def __init__(self, barcode, name, price, producer):
        self.barcode = barcode
        self.name = name
        self.producer = producer
        self.price = price
        self.sequential_product_row_number = Product.sequential_product_row_counter
        Product.sequential_product_row_counter += 1

    def generateRow(self):
        product_row = [ 
            sg.pin(
                sg.Col( [[
                    sg.Text(self.producer), 
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
    def __init__(self, database_caller):
        self.database_caller = database_caller
        self.products_list = []
        self.user = None

    def reset(self):
        self.user = None
        self.products_list = []

    def checkout(self):
        checkout_ready = not (self.user == None) and self.products_list
        if checkout_ready:
            return self.database_caller.insertCheckout(self.products_list, self.user)
        else:
            return False

    def removeProductByRowNumber(self, row_number):
        for product in self.products_list:
            if product.sequential_product_row_number == row_number:
                self.products_list.remove(product)

    def refreshUser(self):
        if self.user:
            self.user = self.database_caller.getUserFromDatabase(self.user.barcode)
