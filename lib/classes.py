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
            self.user = self.database_caller.calculateAndUpdateUserBalance(self.user)
            new_balance = self.user.current_balance
            for product in self.products_list:
                new_balance -= product.price
            self.database_caller.beginTransaction()
            transaction_complete = self.database_caller.insertPurchasesList(self.products_list, self.user)
            transaction_complete &= self.database_caller.updateUserBalance(self.user, new_balance)
            if transaction_complete:
                self.user = self.database_caller.calculateAndUpdateUserBalance(self.user)
                return self.database_caller.commitCurrentTransaction()
            else:
                return False

    def removeProductByRowNumber(self, row_number):
        for product in self.products_list:
            if product.sequential_product_row_number == row_number:
                self.products_list.remove(product)

    def refreshUser(self):
        if self.user:
            self.user = self.database_caller.getUserFromDatabase(self.user.barcode)
